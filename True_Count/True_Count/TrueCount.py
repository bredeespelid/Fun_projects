import tkinter as tk

class BlackjackCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Counter")

        self.running_count = 0
        self.num_decks = 1  # Default number of decks
        self.cards_per_deck = 52  # Initial value (will be updated dynamically)
        self.drawn_cards = 0  # Initially no cards drawn

        # GUI elements
        self.label_count = tk.Label(root, text=f"Running Count: {self.running_count}")
        self.label_count.grid(row=1, column=0, padx=10, pady=10)

        self.label_decks = tk.Label(root, text="Number of Decks:")
        self.label_decks.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.entry_decks = tk.Entry(root)
        self.entry_decks.insert(0, self.num_decks)
        self.entry_decks.grid(row=0, column=1, padx=10, pady=10)
        self.entry_decks.bind("<Return>", self.update_deck_info)  # Bind Enter key to update deck info

        self.label_cards_in_deck = tk.Label(root, text="")
        self.label_cards_in_deck.grid(row=2, column=0, padx=10, pady=10)

        self.label_remaining_cards = tk.Label(root, text="")
        self.label_remaining_cards.grid(row=2, column=1, padx=10, pady=10)

        # Frame to hold buttons horizontally
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # Buttons for card categories
        self.button_2_6 = tk.Button(self.button_frame, text="2-6 (+1)", width=10, padx=5, pady=5)
        self.button_2_6.grid(row=0, column=0, padx=5, pady=5)
        self.button_2_6.bind("<Button-1>", lambda event, value=1: self.on_button_click(event, value))

        self.button_7_9 = tk.Button(self.button_frame, text="7-9 (0)", width=10, padx=5, pady=5)
        self.button_7_9.grid(row=0, column=1, padx=5, pady=5)
        self.button_7_9.bind("<Button-1>", lambda event, value=0: self.on_button_click(event, value))

        self.button_10_Ace = tk.Button(self.button_frame, text="10-Ace (-1)", width=10, padx=5, pady=5)
        self.button_10_Ace.grid(row=0, column=2, padx=5, pady=5)
        self.button_10_Ace.bind("<Button-1>", lambda event, value=-1: self.on_button_click(event, value))

        self.button_reset = tk.Button(root, text="Reset", command=self.reset_count)
        self.button_reset.grid(row=4, column=0, columnspan=2, pady=10)

        self.stats_label = tk.Label(root, text="")
        self.stats_label.grid(row=1, column=1, padx=10, pady=10)

        self.update_labels()

        # Bind keyboard keys to button clicks
        self.root.bind('1', lambda event: self.button_2_6.invoke())
        self.root.bind('2', lambda event: self.button_7_9.invoke())
        self.root.bind('3', lambda event: self.button_10_Ace.invoke())

    def on_button_click(self, event, value):
        self.update_running_count(value)
        self.drawn_cards += 1  # Increment drawn cards
        self.update_labels()

    def update_running_count(self, value):
        self.running_count += value

    def reset_count(self):
        self.running_count = 0
        self.drawn_cards = 0
        self.update_labels()

    def update_labels(self):
        self.num_decks = int(self.entry_decks.get())
        self.cards_per_deck = 52 * self.num_decks  # Total cards in all decks
        self.remaining_cards = self.cards_per_deck - self.drawn_cards  # Calculate remaining cards

        self.label_count.config(text=f"Running Count: {self.running_count}")
        self.label_cards_in_deck.config(text=f"Cards in Deck: {self.cards_per_deck}")
        self.label_remaining_cards.config(text=f"Remaining Cards: {self.remaining_cards}")

        true_count = self.running_count / (self.remaining_cards / 52) if self.remaining_cards > 0 else 0
        self.stats_label.config(text=f"True Count: {true_count:.2f}")

    def update_deck_info(self, event):
        self.num_decks = int(self.entry_decks.get())
        self.cards_per_deck = 52 * self.num_decks
        self.drawn_cards = 0  # Reset drawn cards when number of decks is updated
        self.update_labels()

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackCounterApp(root)
    root.mainloop()
