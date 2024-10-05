import os
import json
import random
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

# Path to folder containing vocabulary text files
VOCAB_FOLDER = 'vocab_folder'
STATE_FILE = 'state.json'
MIN_WORDS = 10  # You want to learn at least 10 words each session

# Spaced repetition intervals in days
INTERVALS = [1, 2, 4, 7, 15, 30]  # Example intervals: 1, 2, 4, 7, 15, 30 days

def load_words(folder):
    words = []
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            with open(os.path.join(folder, filename), 'r') as file:
                words.extend([line.strip() for line in file if line.strip()])
    return words

def load_state(state_file):
    if os.path.exists(state_file):
        with open(state_file, 'r') as file:
            return json.load(file)
    return {'words': {}, 'review_today': []}

def save_state(state, state_file):
    with open(state_file, 'w') as file:
        json.dump(state, file, indent=4)

def schedule_word(word):
    next_review_date = datetime.now().date() + timedelta(days=INTERVALS[0])
    return {
        'word': word,
        'interval_idx': 0,
        'next_review': next_review_date.isoformat()
    }

def update_schedule(word_info):
    if word_info['interval_idx'] < len(INTERVALS) - 1:
        word_info['interval_idx'] += 1
    word_info['next_review'] = (datetime.now().date() + timedelta(days=INTERVALS[word_info['interval_idx']])).isoformat()

def prepare_review_list(state):
    today = datetime.now().date().isoformat()
    review_today = [word_info for word_info in state['words'].values() if word_info['next_review'] == today]
    
    if len(review_today) < MIN_WORDS:
        remaining_words = [word_info for word_info in state['words'].values() if word_info not in review_today]
        additional_words = random.sample(remaining_words, min(MIN_WORDS - len(review_today), len(remaining_words)))
        review_today.extend(additional_words)

    state['review_today'] = review_today

def add_new_words(state, words):
    for word in words:
        if word not in state['words']:
            state['words'][word] = schedule_word(word)

class FlashcardApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Load words and state
        self.words = load_words(VOCAB_FOLDER)
        self.state = load_state(STATE_FILE)
        add_new_words(self.state, self.words)
        prepare_review_list(self.state)

        if not self.state['review_today']:
            layout.add_widget(Label(text="No words to review today!"))
        else:
            for word_info in self.state['review_today']:
                word_label = Label(text=word_info['word'], font_size=24)
                layout.add_widget(word_label)
                
                # Button to go to the next word and update the schedule
                next_button = Button(text="Next", size_hint=(1, 0.2))
                next_button.bind(on_press=self.next_word)
                layout.add_widget(next_button)

        return layout

    def next_word(self, instance):
        if self.state['review_today']:
            current_word = self.state['review_today'].pop(0)
            update_schedule(current_word)
            save_state(self.state, STATE_FILE)
            self.root.clear_widgets()  # Clear the screen for the next word
            self.build()  # Rebuild the layout for the next word

if __name__ == "__main__":
    FlashcardApp().run()
