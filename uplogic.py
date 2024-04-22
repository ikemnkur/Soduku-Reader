import bge
from collections import OrderedDict
from uplogic.ui import Canvas
from uplogic.ui import RelativeLayout
from uplogic.ui import BoxLayout
from uplogic.ui import LabelButton
from uplogic.ui import Cursor
from uplogic.ui import Image
from uplogic.ui import TextInput
from uplogic.input import MouseLook
from uplogic.input import key_press
from uplogic.decorators import game_props
from uplogic.utils import world_to_screen
from mathutils import Vector


###################################################
# TESTED IN UPBGE 0.36 / uplogic 1.8.2
###################################################
# This file demonstrates some basic UI functions
#
# A Canvas is the general drawing entity to which
# other widgets need to be added.
#
# Widgets can also be added to other widgets, as
# long as the relation leads to a Canvas.
#
# Each widget can be set to visible or invisible
# using the 'show' attribute.
# Other attributes like 'size', 'pos' or 'bg_color'
# can also be set after the Widget has been added
# to a parent.
#
# The Cursor object is unique in that it does not
# need a Canvas, it manages itself and only needs
# to be created once. The cursor texture can also
# be changed afterwards.
###################################################


# "@game_props" line the component that "self.show_menu" should be reading and writing
# into the property "show_menu" on the owner of this component.
@game_props('show_menu')
class UI(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.mouselook = MouseLook(self.object, self.object.children['Head'], use_cap_y=True)

        # Build Floating UI
        self.floating_ui = Canvas()
        
        self.reticle = RelativeLayout(
            relative={'pos': True},
            pos=[.5, .5], size=[4, 4],
            halign='center',
            valign='center',
            bg_color=(1, 1, 1, 1)
        )

        # This is the triangle marker above the moving Suzanne
        self.UI_marker = Image(
            relative={'pos': True},
            size=[40, 40],
            texture='UIMarker.png',
            halign='center',
            valign='center'
        )

        # This is the button on the static Suzanne
        self.suzanne_button = LabelButton(
            relative={'pos': True},
            size=[100, 100],
            halign='center',
            valign='top',
            bg_color=(1, .5, 0, .5),
            text='Click Me',
            hover_color=[1, .5, 0, 1]
        )
        # Defining an action for the button
        self.suzanne_button.on_click = self.rotate_suzanne

        # Order is important for drawing - last object is always on top
        self.floating_ui.add_widget(self.UI_marker)
        self.floating_ui.add_widget(self.suzanne_button)
        self.floating_ui.add_widget(self.reticle)

        # Build Menu UI
        self.menu = Canvas()
        
        self.frame = RelativeLayout(
            relative={'pos': True, 'size': True},
            pos=[.1, .1],
            size=[.8, .8],
            bg_color=[0, 0, 0, .5],
            border_width=1,
            border_color=[1, 1, 1, 1]
        )

     
        
    # Left Menu
        self.left_menu = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[0, 0],
            size=[.2, 1],
            bg_color=[0, 0, 0, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )

        # return to game button
        self.return_button = LabelButton(
            relative={'size': True, 'pos': True},
            pos=[1, 1],
            size=[1, .1],
            bg_color=[0, 0, 0, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='Return'
        )
        self.return_button.on_click = self.set_menu_false

        # quit game button
        self.quit_button = LabelButton(
            relative={'size': True, 'pos': True},
            pos=[1, 1],
            size=[1, .1],
            bg_color=[0, 0, 0, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='Quit'
        )
        self.quit_button.on_click = self.quit

        # info button
        self.info_button = LabelButton(
            relative={'size': True, 'pos': True},
            pos=[1, 1],
            size=[1, .1],
            bg_color=[0, 0, 0, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='Debug Info'
        )
        self.info_button.on_click = self.showInfo

    # right window content
        self.right_window = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[.2, 0],
            size=[.8, 1],
            bg_color=[0, 0, .2, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )
       # info text
        self.info_button = TextInput(
            relative={'pos': True},
            pos=[1, 1],
            font_color=[1, 1, 1, 1],
            font_size=20,
            shadow = True,
            shadow_color=[0, 0.1, 0.1, 1],
            text='Search'
        )

    # exit menu button
        self.x_button = LabelButton(
            relative={'pos': True},
            pos=[1, 1],
            size=[20, 20],
            halign='right',
            valign='top',
            bg_color=[0, 0, 0, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='X'
        )

        self.x_button.on_click = self.set_menu_false
        
        
    # Add all widgets to the menu 
        self.menu.show = False
        self.menu.add_widget(self.frame)

        self.frame.add_widget(self.left_menu)
        self.frame.add_widget(self.right_window)
        self.frame.add_widget(self.x_button)

        self.left_menu.add_widget(self.return_button)
        self.left_menu.add_widget(self.quit_button)
        self.left_menu.add_widget(self.info_button)

        self.right_window.add_widget(self.info_text)

        self.cursor = Cursor(
            size=[30, 30],
            texture='cursor.png'
        )
        self.cursor.show = False

    def quit(self, *a):
        bge.logic.endGame()
    
    def showInfo(self, *a):
        self.info_button.text = "Working"

    def update(self):
        suzanne = self.object.scene.objects['Suzanne']
        if key_press('esc'):
            self.show_menu = not self.show_menu
            self.floating_ui.show = not self.show_menu
            self.mouselook.active = not self.show_menu
            self.menu.show = self.show_menu
            self.cursor.show = self.show_menu
        if self.show_menu:
            pass
        else:
            self.UI_marker.pos = Vector(world_to_screen(suzanne)) + Vector((0, .1))
            self.suzanne_button.pos = world_to_screen(self.object.scene.objects['Suzanne.001'])
        
        suzanne.applyRotation((0, 0, -.01))
        suzanne.applyMovement((.1, 0, 0), True)
        

    def rotate_suzanne(self, *a):
        self.object.scene.objects['Suzanne.001'].applyRotation((0, 0, 3.1516 * .25))

    def set_menu_false(self, arg):
        self.show_menu = False
        self.floating_ui.show = not self.show_menu
        self.mouselook.active = not self.show_menu
        self.menu.show = self.show_menu
        self.cursor.show = self.show_menu