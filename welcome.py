import pygame
import sys


class WelcomePage:
    def __init__(self, number):
        self.player_number = number
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (173, 216, 230)  # Light blue background
        self.text_color = (255, 255, 255)  # White text
        self.font_name = 'freesansbold.ttf'
        self.colors = [(255, 99, 71), (255, 215, 0), (173, 255, 47), (135, 206, 235), (238, 130, 238)]
        self.current_color_index = 0

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('8 1/2 - Welcome Page')
        self.font_large = pygame.font.Font(self.font_name, 48)
        self.font_medium = pygame.font.Font(self.font_name, 36)
        self.font_small = pygame.font.Font(self.font_name, 24)
        self.font_rules = pygame.font.Font(self.font_name, 18)  # Smaller font for the rules

        self.button_color = (0, 128, 0)
        self.button_hover_color = (0, 255, 0)
        self.button_rect = pygame.Rect((self.screen_width // 2 - 100, 450, 200, 50))

        self.close_button_color = (255, 0, 0)
        self.close_button_hover_color = (255, 99, 71)
        self.close_button_rect = pygame.Rect((self.screen_width - 110, 10, 100, 40))

        self.show_rules = False
        self.scroll_offset = 0

        self.rules_text = [
            "Goal: Be the first to finish your pile of cards",
            "During the game each player will keep 3 cards in his hand,",
            "from which he chooses the one to play. After discarding, the player",
            "will receive new card from his Bank to return the number of cards in",
            "his hand back to three.",
            "Rules: The player holding the lowest yellow card in his hand is given",
            "the honor of playing the first card. This player places that card in",
            "the center to start a discard pile. Play continues going clockwise and",
            "each player must discard one card onto the discard pile. This can be",
            "any card as long as it is HIGHER THAN OR EQUAL TO THE TOP NUMBER in the",
            "discard pile. The player may also use one of the Wild Cards (see \"The 3",
            "Wild Cards\" below), which can be used on almost any number. A player",
            "who cannot play must collect the discard pile – he takes these cards",
            "and puts them aside. These cards will not be played anymore but at the",
            "end of the game they will be counted against him. After a player collects",
            "the discard pile the next player starts a new pile with any card from",
            "their hand.",
            "The 3 Wild Cards: Ghost - The Ghost can be played on any number. It is an",
            "\"invisible\" card that leaves the discard pile unchanged. The next player",
            "should refer to the card underneath. Half - Half may be played on any",
            "number except \"Eight and a Half\" (see \"The Rules of Eight and a Half\").",
            "It \"sticks\" to the number on which it is played and raises the discard",
            "pile by half. Zero - 0 can be played on any whole number. It zeros the",
            "discard pile and the next player may play any number or wild card. 0 cannot",
            "be played when the discard pile is not a whole number (a \"Number and a Half\").",
            "The End of the Game: The winner of the round is the first player to get rid of",
            "all his cards. The player who ends up with the most cards in his possession",
            "(counting the cards collected and the cards that still haven't been played)",
            "among the rest of the players is the Big Loser."
        ]

        self.run_welcome_page()

    def draw_text(self, text, font, color, center):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, text, rect, color, hover_color):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        current_color = hover_color if is_hovered else color
        pygame.draw.rect(self.screen, current_color, rect)
        self.draw_text(text, self.font_small, self.text_color, rect.center)
        return is_hovered

    def draw_rules_overlay(self):
        self.screen.fill((255, 255, 255))  # White background
        y_offset = 50 + self.scroll_offset
        for line in self.rules_text:
            self.draw_text(line, self.font_rules, (0, 0, 0), (self.screen_width // 2, y_offset))
            y_offset += 25

        self.draw_button("Close", self.close_button_rect, self.close_button_color, self.close_button_hover_color)

    # def close(self):
    #     pygame.quit()

    def run_welcome_page(self):
        clock = pygame.time.Clock()
        animation_timer = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.show_rules:
                            if self.close_button_rect.collidepoint(event.pos):
                                self.show_rules = False
                        else:
                            if self.button_rect.collidepoint(event.pos):
                                self.show_rules = True
                elif event.type == pygame.MOUSEWHEEL:
                    if self.show_rules:
                        self.scroll_offset += event.y * 20
                        self.scroll_offset = min(0, self.scroll_offset)  # Prevent scrolling too far up
                        max_scroll = len(self.rules_text) * 25 - self.screen_height + 100
                        self.scroll_offset = max(-max_scroll, self.scroll_offset)  # Prevent scrolling too far down

            self.screen.fill(self.bg_color)

            if self.show_rules:
                self.draw_rules_overlay()
            else:
                self.draw_text("Welcome to 8 1/2!", self.font_large, self.text_color, (self.screen_width // 2, 100))
                self.draw_text(f"Player Number: {self.player_number}", self.font_medium, self.text_color,
                               (self.screen_width // 2, 200))
                self.draw_text("You have joined the game!", self.font_small, self.text_color,
                               (self.screen_width // 2, 300))

                if pygame.time.get_ticks() - animation_timer > 500:  # Change color every 500ms
                    self.current_color_index = (self.current_color_index + 1) % len(self.colors)
                    animation_timer = pygame.time.get_ticks()

                color_rect = pygame.Rect(0, 400, self.screen_width, 100)
                pygame.draw.rect(self.screen, self.colors[self.current_color_index], color_rect)

                self.draw_button("Show Rules", self.button_rect, self.button_color, self.button_hover_color)

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    player_number = 1  # This can be set dynamically based on your application
    WelcomePage(player_number)
