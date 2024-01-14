"""
    Phase ten clone. 
"""

import arcade
import random 

SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960

SCREEN_TITLE = "Phase Ten"

#constants for cards# 
VERTICAL_MARGIN = 0.1
HORIZONTAL_MARGIN = 0.1

CARD_SCALE = 0.10

CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 200 * CARD_SCALE


START_Y = SCREEN_HEIGHT //2 
START_X = SCREEN_WIDTH //2 + CARD_WIDTH

CARD_VALUES = list(range(1, 13))
CARD_COLORS = ["R", "G", "B", "Y"] * 2

XTRA_CARDS = ["W"] * 8 + ["S"]*4

CARDS = []

for color in CARD_COLORS:
    for val in CARD_VALUES:
        CARDS += [str(val)+"-"+color]

CARDS += XTRA_CARDS

#Constants for the deck
deck_size = len(CARDS)
deck_cards = list(range(0,deck_size))

DECK_X_POSITION = SCREEN_WIDTH * 3/4
DECK_Y_POSITION = SCREEN_HEIGHT //2

#constants for discard pile
DISCARD_POS_X = SCREEN_WIDTH * 1/4
DISCARD_POS_Y = DECK_Y_POSITION

#Other Player Data
num_of_players = 3 #not including user 
ENEMY_PLAY_AREA_X = SCREEN_WIDTH//2  
ENEMY_PLAY_AREA_WIDTH = SCREEN_WIDTH - SCREEN_WIDTH * 2* HORIZONTAL_MARGIN
ENEMY_PLAY_AREA_Y = SCREEN_HEIGHT * 5/6 + VERTICAL_MARGIN*SCREEN_HEIGHT*0.5
ENEMY_PLAY_AREA_HEIGHT = (1-2*VERTICAL_MARGIN) * SCREEN_HEIGHT * 1/3
enemy_objectives = [2 for i in range(num_of_players)] 

#Player Area
num_of_objectives = 2 #can be 1,2
PLAYER_AREA_X = SCREEN_WIDTH//2
PLAYER_AREA_Y = SCREEN_HEIGHT * 1/6 
PLAYER_CARDS_X = SCREEN_WIDTH//2
PLAYER_CARDS_Y = SCREEN_HEIGHT * 11/12 
objective_x = SCREEN_WIDTH//2 
objective_y = SCREEN_HEIGHT * 1/4 + VERTICAL_MARGIN*SCREEN_HEIGHT*0.5

class Card(arcade.Sprite):
    """Card Sprite"""
    def __init__(self, col, value, width = CARD_WIDTH, height = CARD_HEIGHT ):
        
        self.col = col
        self.value = value 
        self.image_file_name = f"resources\{self.value}{self.col}Card.png"
        super().__init__(self.image_file_name, CARD_SCALE, hit_box_algorithm= "None")



class PhaseGame(arcade.Window):
    """ Main app class"""
    def __init__(self): 
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #sprite list of the cards
        self.card_list = None

        arcade.set_background_color(arcade.color.ALMOND)
        # Cards that are being dragged by the player
        self.held_cards = None 

        # Card origin 
        self.held_cards_original_position = None 

        #Sprite list of with all the mats the cards lay on 
        self.pile_mat_list = None 

    def setup(self):
        """Set up the game, call to reset the game"""
        #card on mouse
        self.held_cards = []
        #card's og location
        self.held_cards_original_position = []

        #-- Create the mats 

        #Sprite list with all mats 
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        #Create the mats for the deck 
        pile = arcade.SpriteSolidColor(int(CARD_WIDTH*5.5), int(CARD_HEIGHT*5.5), arcade.csscolor.BEIGE)
        pile.position = DECK_X_POSITION, DECK_Y_POSITION
        self.pile_mat_list.append(pile)
        #Create the discard pile list
        pile = arcade.SpriteSolidColor(int(CARD_WIDTH*5.5), int(CARD_HEIGHT*5.5), arcade.csscolor.BEIGE)
        pile.position = DISCARD_POS_X, DISCARD_POS_Y
        self.pile_mat_list.append(pile)
        #create the player hand list 
        pile = arcade.SpriteSolidColor(int(CARD_WIDTH*35), int(CARD_HEIGHT*5.5), arcade.csscolor.BEIGE)
        pile.position = PLAYER_AREA_X, PLAYER_AREA_Y
        self.pile_mat_list.append(pile)
        #create the player objective list 
        if num_of_objectives == 1: 
            pile = arcade.SpriteSolidColor(int(CARD_WIDTH*35), int(CARD_HEIGHT*5.5), arcade.csscolor.LIGHT_GOLDENROD_YELLOW)
            pile.position = objective_x, objective_y
            self.pile_mat_list.append(pile)
        else:
            for n in range(num_of_objectives):
                x_pos = objective_x//(num_of_objectives) + n * objective_x * 2// num_of_objectives
                pile = arcade.SpriteSolidColor(int(CARD_WIDTH*35//num_of_objectives), int(CARD_HEIGHT*5.5), arcade.csscolor.LIGHT_GOLDENROD_YELLOW)
                pile.position = x_pos, objective_y
                self.pile_mat_list.append(pile)
        #create the enemy area: 
        for n in range(num_of_players):
            x_pos = ENEMY_PLAY_AREA_X // (num_of_players) + n * ENEMY_PLAY_AREA_X * 2// num_of_players
            pile = arcade.SpriteSolidColor(int(CARD_WIDTH * 35// num_of_players), int(CARD_HEIGHT*5.5), arcade.csscolor.LIGHT_CORAL)
            pile.position = x_pos, ENEMY_PLAY_AREA_Y
            self.pile_mat_list.append(pile)


        #create the enemy objective area:
        for n in range(num_of_players):
            x_pos = ENEMY_PLAY_AREA_X // (num_of_players) + n * ENEMY_PLAY_AREA_X * 2// num_of_players
            y_pos = ENEMY_PLAY_AREA_Y
            for m in range(enemy_objectives[n]):
                if m == 0: 
                    translate_y = int(CARD_HEIGHT * 4.5 * (1 + VERTICAL_MARGIN))
                else: 
                    translate_y = int(CARD_HEIGHT * 2.5* (1+VERTICAL_MARGIN))
                y_pos -= translate_y
                pile = arcade.SpriteSolidColor(int(CARD_WIDTH * 35// num_of_players), int(CARD_HEIGHT*2.5), arcade.csscolor.LIGHT_PINK)
                pile.position = x_pos, y_pos 
                self.pile_mat_list.append(pile)
               
        self.card_list = arcade.SpriteList()
        random.shuffle(deck_cards)

        for i in range(deck_size):
            num = deck_cards[i]
            c = CARDS[num]
            if num < 96: 
                c_color = c[-1]
                c_value = c.split('-')[0]
            else: 
                c_color = "Bl" #black
                c_value = c
            card = Card(c_color, c_value, DECK_X_POSITION, START_Y)
            card.position = DECK_X_POSITION, START_Y 
            self.card_list.append(card)
    def pull_to_top(self, card:arcade.Sprite):
        """Pull card to top of the rendering order"""
        #remove and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)


         
    def on_draw(self): 
        """ Render the game screen"""
        self.clear()
        self.pile_mat_list.draw()
        self.card_list.draw()
        
    def on_mouse_press(self, x, y, button, key_modifiers):
        """Called when the user presses a mouse button"""
        cards = arcade.get_sprites_at_point((x,y), self.card_list)
        if len(cards) > 0: 
            primary_card = cards[-1]
            self.held_cards = [primary_card]
            self.held_cards_original_position = [self.held_cards[0].position]
            self.pull_to_top(self.held_cards[0])

    def on_mouse_release(self, x, y, button, key_modifiers):
        """Called when the user releases a mouse button"""
        if len(self.held_cards) == 0: 
            return 
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_pos = True

        if arcade.check_for_collision(self.held_cards[0], pile): 

            for i, dropped_card in enumerate(self.held_cards): 
                dropped_card.position = pile.center_x, pile.center_y
                ratio = dropped_card.width / dropped_card.height
                dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)
                dropped_card.width = dropped_card.height * ratio
                 
            reset_pos = False
        if reset_pos: 
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]
        
        self.held_cards = []

    def on_mouse_motion(self, x:float, y:float, dx:float, dy: float):
        """User moves mouse"""
        #move a held card with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

def main(): 
    """Main program"""
    window = PhaseGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
