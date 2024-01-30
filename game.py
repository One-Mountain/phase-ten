"""
    Phase ten clone. 
"""

import arcade
import arcade.gui
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
# button
BUTTON_WIDTH = int(CARD_WIDTH * 3/4 *10)
BUTTON_HEIGHT = int(CARD_HEIGHT)

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

#CONSTANTS FOR PLAY AREAS(player, deck, discard, player objectives, enemy, and enemy objectives)
PILE_COUNT = 14
DECK_PILE = 0
DISCARD_PILE = 1
PLAYER_PILE = 2 
OBJECTIVE_PILE1 = 3
OBJECTIVE_PILE2 = 4
ENEMY1_PILE = 5
ENEMY1_OBJ1 = 6
ENEMY1_OBJ2 = 7
ENEMY2_PILE = 8
ENEMY2_OBJ1 = 9
ENEMY2_OBJ2 = 10
ENEMY3_PILE = 11
ENEMY3_OBJ1 = 12
ENEMY3_OBJ2 = 13

class Player:
    '''Player class
    keeps track of points, phase, skipped, and objective 
    '''
    def __init__(self, turn): 
        self.turn = turn 
        self.points = 0 
        self.phase = 1
        self.objective_complete = False
        self.skipped = False 
        access = [0]*PILE_COUNT
        self.draw_grab = access[::1]
        self.draw_grab[DECK_PILE], self.draw_grab[DISCARD_PILE] = 1, 1
        self.draw_drop = access[::1] 
        self.draw_drop[3*self.turn - 1] = 1
        self.action_grab = [1 if 3*self.turn-1 <= x <= 3*self.turn+1 else 0 for x in range(PILE_COUNT)]
        self.action_drop = self.action_grab[::1] 
        self.action_drop[DISCARD_PILE] = 1
        self.action2_grab = access[::1]
        self.action2_grab[3*self.turn - 1] = 1
        self.action2_drop = self.action_drop[::1]
    
        


class Card(arcade.Sprite):
    """Card Sprite"""
    def __init__(self, col, value, width = CARD_WIDTH, height = CARD_HEIGHT ):
        
        self.col = col
        self.value = value 
        self.image_file_name = f"phase-ten\\resources\{self.value}{self.col}Card.png"
        super().__init__(self.image_file_name, CARD_SCALE, hit_box_algorithm= "None")
        #Create a list of lists, each holds a pile of cards
        self.piles = None 


class PhaseGame(arcade.Window):
    """ Main app class"""
    def __init__(self): 
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        #Required parameters for UI elements like buttons
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        #Create a BOX 
        self.v_box = arcade.gui.UIBoxLayout()
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
        #turn: 0 is shuffle, 1 is player, 2-4 is enemy player turn if applicable
        self.turn = 0
        self.maxTurn = 1 + num_of_players
        self.turn_sequence = 0 #draw phase, action_phase, discard_hand_phase

        #phases
        phases = random.randint(3,6)

        #card on mouse
        self.held_cards = []
        #card's og location
        self.held_cards_original_position = []

        #-- Create the mats 

        #Sprite list with all mats 
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()
        for i in range(PILE_COUNT):
            p = arcade.SpriteSolidColor(1, 1, arcade.csscolor.BLACK)
            p.position = SCREEN_WIDTH*2, SCREEN_HEIGHT*2
            self.pile_mat_list.append(p)
        
        #Create the mats for the deck 
        pile = arcade.SpriteSolidColor(int(CARD_WIDTH*5.5), int(CARD_HEIGHT*5.5), arcade.csscolor.BEIGE)
        pile.position = DECK_X_POSITION, DECK_Y_POSITION
        self.pile_mat_list[DECK_PILE] =  pile
        #Create the discard pile list
        pile = arcade.SpriteSolidColor(int(CARD_WIDTH*5.5), int(CARD_HEIGHT*5.5), arcade.csscolor.BEIGE)
        pile.position = DISCARD_POS_X, DISCARD_POS_Y
        self.pile_mat_list[DISCARD_PILE] =  pile
        #create the player hand list 
        pile = arcade.SpriteSolidColor(int(CARD_WIDTH*35), int(CARD_HEIGHT*5.5), arcade.csscolor.BEIGE)
        pile.position = PLAYER_AREA_X, PLAYER_AREA_Y
        self.pile_mat_list[PLAYER_PILE] = pile
        #create the player objective list 
        if num_of_objectives == 1: 
            pile = arcade.SpriteSolidColor(int(CARD_WIDTH*35), int(CARD_HEIGHT*5.5), arcade.csscolor.LIGHT_GOLDENROD_YELLOW)
            pile.position = objective_x, objective_y
            self.pile_mat_list[OBJECTIVE_PILE1]=  pile
        else:
            for n in range(num_of_objectives):
                x_pos = objective_x//(num_of_objectives) + n * objective_x * 2// num_of_objectives
                pile = arcade.SpriteSolidColor(int(CARD_WIDTH*35//num_of_objectives), int(CARD_HEIGHT*5.5), arcade.csscolor.LIGHT_GOLDENROD_YELLOW)
                pile.position = x_pos, objective_y
                if n == 0: 
                    self.pile_mat_list[OBJECTIVE_PILE1] = pile
                else: 
                    self.pile_mat_list[OBJECTIVE_PILE2] = pile
        #create the confirm button for objectives:
        button_x_pos = objective_x*7/4
        button_y_pos = objective_y + CARD_HEIGHT//2 
        confirm_button = arcade.gui.UIFlatButton(text= "Confirm", width = BUTTON_WIDTH, height = BUTTON_HEIGHT, x = button_x_pos, y = button_y_pos)
        self.v_box.add(confirm_button.with_space_around(bottom = 10))

        confirm_button.on_click = self.on_click_confirm
        
        peek_button = arcade.gui.UIFlatButton(text="Peek", width = BUTTON_WIDTH, height = BUTTON_HEIGHT)
        self.v_box.add(peek_button)
        peek_button.on_click = self.on_click_peek


        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x = "center_x",
                                      anchor_y = "center_y",
                                      align_x = 12*CARD_WIDTH,
                                      align_y = -5*CARD_HEIGHT, 
                                      child = self.v_box)
        )

        #create the enemy area: 
        for n in range(num_of_players):
            x_pos = ENEMY_PLAY_AREA_X // (num_of_players) + n * ENEMY_PLAY_AREA_X * 2// num_of_players
            pile = arcade.SpriteSolidColor(int(CARD_WIDTH * 35// num_of_players), int(CARD_HEIGHT*5.5), arcade.csscolor.LIGHT_CORAL)
            pile.position = x_pos, ENEMY_PLAY_AREA_Y
            self.pile_mat_list[3*n+5] = pile


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
                self.pile_mat_list[3*n+6+m] = pile
            
        self.card_list = arcade.SpriteList()

        #SHUFFLE CARDS
        if self.turn == 0: 
            random.shuffle(deck_cards)
            self.turn += 1

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
        # Create the list of list, each holds a pile of cards. 
        self.piles = [[] for _ in range(PILE_COUNT)]

        #Put the cards in the deck pile 
        for card in self.card_list:
            self.piles[DECK_PILE].append(card)
        
        #initialize players
        self.player_list = []
        for p in range(num_of_players+1):
            if p == 0: 
                player1 = Player(turn = p+1)
                self.player_list.append(player1)
            else: 
                player = Player(turn = p+1)
                self.player_list.append(player)
        self.deal_cards() 

    
    def deal_cards(self):
        for c in range(10): #give each player their starting hand
            for hand in range(num_of_players+1): #ten cards per player
                #take it out of the deck pile
                card = self.piles[DECK_PILE].pop()
                #put in on the player's pile
                self.piles[3*hand+2].append(card)
                card.position = self.pile_mat_list[3*hand+2].position
                
    def on_click_confirm(self, event): 
        print("CONFIRMED")
    def on_click_peek(self, event):
        print("you peeked!")
    def get_pile_for_card(self, card): 
        #which pile is the card in? #
        for index, pile in enumerate(self.piles):
            if card in pile: 
                return index 

    def remove_card_from_pile(self, card): 
        for pile in self.piles: 
            if card in pile: 
                pile.remove(card)
                break 

    def move_card_to_new_pile(self, card, pile_index):
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)


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
        self.manager.draw()
        
    def on_mouse_press(self, x, y, button, key_modifiers):
        """Called when the user presses a mouse button"""
        current_player = self.player_list[self.turn-1]
        if self.turn_sequence == 0: # the draw phase
            check_able_list = current_player.draw_grab 
        elif self.turn_sequence == 1: # the action phase
            check_able_list = current_player.action_grab
        else: 
            check_able_list = current_player.action2_grab
        cards = arcade.get_sprites_at_point((x,y), self.card_list)
        if len(cards) > 0: 
            primary_card = cards[-1]
            pile_index = self.get_pile_for_card(primary_card)
            if check_able_list[pile_index] == 1: 
                self.held_cards = [primary_card]
                self.held_cards_original_position = [self.held_cards[0].position]
                self.pull_to_top(self.held_cards[0])
            else: 
                cards = []

    def on_mouse_release(self, x, y, button, key_modifiers):
        """Called when the user releases a mouse button"""
        if len(self.held_cards) == 0: 
            return 
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_pos = True
        current_player = self.player_list[self.turn-1]
        if self.turn_sequence == 0:  #draw phase: 
            check_able_list = current_player.draw_drop
        elif self.turn_sequence == 1: #action phase 
            check_able_list = current_player.action_drop 
        else: 
            check_able_list = current_player.action2_drop
        
        if arcade.check_for_collision(self.held_cards[0], pile): 
            #what pile is it
            no_spread = [DECK_PILE, DISCARD_PILE, ENEMY1_PILE, ENEMY2_PILE, ENEMY3_PILE]
            enemy_piles = [ENEMY1_PILE,ENEMY2_PILE, ENEMY3_PILE]
            pile_index = self.pile_mat_list.index(pile)

            #same pile it started in
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                pass

            elif pile_index not in no_spread and check_able_list[pile_index]==1: 
                if len(self.piles[pile_index]) >0:
                    w = len(self.piles[pile_index]) 
                    for i, c in enumerate(self.piles[pile_index]):
                        loc_x = pile.center_x - pile.width//2 + (i+1)*pile.width/(w+2)
                        c.position = loc_x, pile.center_y
                    for i, dropped_card in enumerate(self.held_cards):
                        loc_x = pile.center_x - pile.width//2 + (w+1)*pile.width/(w+2)
                        dropped_card.position = loc_x, pile.center_y
                        ratio = dropped_card.width / dropped_card.height
                        dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)
                        dropped_card.width = dropped_card.height * ratio
                else: 
                    for i, dropped_card in enumerate(self.held_cards): 
                        dropped_card.position = pile.center_x, pile.center_y
                        ratio = dropped_card.width / dropped_card.height
                        dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)
                        dropped_card.width = dropped_card.height * ratio
                for card in self.held_cards: 
                    self.move_card_to_new_pile(card, pile_index)
                
                reset_pos = False
            elif pile_index in enemy_piles and check_able_list[pile_index]==1:
                if len(self.piles[pile_index]) > 0: 
                    w = len(self.piles[pile_index])
                    if w <= 4: 
                        for i, c in enumerate(self.piles[pile_index]): 
                            loc_x = pile.center_x -pile.width//2 + (i+1)* pile.width/(w+2)
                            c.position = loc_x, pile.center_y 
                        for i, dropped_card in enumerate(self.held_cards):
                            loc_x = pile.center_x - pile.width//2 + (w+1)*pile.width/(w+2)
                            dropped_card.position = loc_x, pile.center_y
                            ratio = dropped_card.width / dropped_card.height
                            dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)
                            dropped_card.width = dropped_card.height * ratio
                    else: 
                        for i, c in enumerate(self.piles[pile_index]):
                            ww = 5
                            loc_x = pile.center_x - pile.width//2 + (i%5+1)*pile.width/(ww+2)
                            loc_y = pile.center_y - pile.height//4 + pile.height/2 * (i//5)
                            c.position = loc_x, loc_y
                            ratio = c.width / c.height
                            c.height = pile.height * (1-2*VERTICAL_MARGIN)//2 
                            c.width = c.height * ratio
                        for i, dropped_card in enumerate(self.held_cards):
                            loc_x = pile.center_x - pile.width//2 + (w%5+1)*pile.width/(ww+2)
                            loc_y = pile.center_y - pile.height//4 + pile.height/2 
                            dropped_card.position = loc_x, loc_y
                            ratio = dropped_card.width / dropped_card.height 
                            dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)//2 
                            dropped_card.width = dropped_card.height * ratio 
                else: 
                    for i, dropped_card in enumerate(self.held_cards): 
                        dropped_card.position = pile.center_x, pile.center_y
                        ratio = dropped_card.width / dropped_card.height
                        dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)
                        dropped_card.width = dropped_card.height * ratio
                for card in self.held_cards: 
                    self.move_card_to_new_pile(card, pile_index)
                reset_pos = False

            elif check_able_list[pile_index] == 1: 
                for i, dropped_card in enumerate(self.held_cards): 
                    dropped_card.position = pile.center_x, pile.center_y
                    ratio = dropped_card.width / dropped_card.height
                    dropped_card.height = pile.height * (1-2*VERTICAL_MARGIN)
                    dropped_card.width = dropped_card.height * ratio
                for card in self.held_cards: 
                    self.move_card_to_new_pile(card, pile_index)
                
                reset_pos = False 

            if check_able_list[pile_index] == 1 and self.turn_sequence == 0 and not reset_pos: #draw phase ends 
                if current_player.objective_complete: 
                    self.turn_sequence = 2
                else: 
                    self.turn_sequence = 1
            elif pile_index == DISCARD_PILE and self.turn_sequence == 1 and not reset_pos: #action phase ends no clear
                ##################### CHECK FOR CARDS IN THE OBJECTIVE PILES
                self.turn_sequence = 0
                self.turn += 1
                if self.turn > self.maxTurn: 
                    self.turn = 1
                print("Turn", self.turn)
            elif pile_index == DISCARD_PILE and self.turn_sequence == 2 and not reset_pos: #action phase ends 
                ##### CHECK FOR WIN CONDITION#### 
                self.turn_sequence = 0 
                self.turn +=1
                if self.turn > self.maxTurn: 
                    self.turn = 1
                print("Turn", self.turn)
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
