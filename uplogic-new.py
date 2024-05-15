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

        self.left_menu = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[0, 0],
            size=[.2, 1],
            bg_color=[0, 0, 0, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )

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

        self.right_window = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[.2, 0],
            size=[.8, 1],
            bg_color=[0, 0, .2, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )

        self.right_textLayout = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[.5, .4],
            size=[.8, 0.1],
            bg_color=[0, .6, .2, 0.25],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )
        
        self.info_text = TextInput(
            relative={'pos': False},
            pos=[.5, .1],
            font_color=[1, 1, 1, 1],
            font_size=20,
            shadow = True,
            shadow_color=[0, 0.1, 0.1, 1],
            text='Search'
        )
        
        self.main_text = TextInput(
            relative={'pos': True},
            pos=[.5, .5],
            font_color=[1, 1, 1, 1],
            font_size=14,
            shadow = True,
            shadow_color=[0, 0.1, 0.1, 1],
            text='Info'
        )

        self.x_button = LabelButton(
            relative={'pos': True},
            pos=[1, 1],
            size=[20, 20],
            halign='right',
            valign='top',
            bg_color=[1, 0, 0, 1],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='X'
        )
        self.x_button.on_click = self.set_menu_false
        
        self.menu.show = False
        self.menu.add_widget(self.frame)
        self.frame.add_widget(self.left_menu)
        self.frame.add_widget(self.right_window)
        self.frame.add_widget(self.x_button)
        self.left_menu.add_widget(self.return_button)
        self.left_menu.add_widget(self.quit_button)
        self.left_menu.add_widget(self.info_button)
        self.right_window.add_widget(self.right_textLayout)
        self.right_textLayout.add_widget(self.info_text)
        self.right_textLayout.add_widget(self.main_text)
        self.cursor = Cursor(size=[30, 30], texture='cursor.png')
        self.cursor.show = False

        self.objects_info = self.store_objects_info()
        self.add_game_objects_ui()

    def add_game_objects_ui(self):
        objects = bge.logic.getCurrentScene().objects
        for obj in objects:
            object_layout = BoxLayout(
                relative={'pos': True, 'size': True},
                pos=[0, 0],
                size=[1, .1],
                bg_color=[0, 0, 0, 0],
                orientation='horizontal'
            )

            edit_button = LabelButton(
                relative={'size': True, 'pos': True},
                pos=[0, 0],
                size=[.2, 1],
                bg_color=[0, 0, 0, 0],
                border_width=1,
                border_color=[1, 1, 1, 1],
                text='Edit'
            )
            edit_button.on_click = self.edit_object

            show_button = LabelButton(
                relative={'size': True, 'pos': True},
                pos=[.2, 0],
                size=[.2, 1],
                bg_color=[0, 0, 0, 0],
                border_width=1,
                border_color=[1, 1, 1, 1],
                text='Show' if obj.visible else 'Hide'
            )
            show_button.on_click = lambda *a, obj=obj: self.toggle_visibility(obj, show_button)

            object_name = LabelButton(
                relative={'size': True, 'pos': True},
                pos=[.4, 0],
                size=[.6, 1],
                bg_color=[0, 0, 0, 0],
                border_width=1,
                border_color=[1, 1, 1, 1],
                text=obj.name
            )
            object_name.on_click = lambda *a, obj=obj: self.display_object_info(obj)

            object_layout.add_widget(edit_button)
            object_layout.add_widget(show_button)
            object_layout.add_widget(object_name)

            self.right_window.add_widget(object_layout)

    def display_object_info(self, obj):
        obj_info = self.get_object_info(obj)
        display_text = "\n".join([f"{key}: {value}" for key, value in obj_info.items()])
        
        # Create the new overlay layout
        self.info_layout = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[0.1, 0.1],
            size=[0.8, 0.8],
            bg_color=[0, 0, 0, 0.8],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )

        exit_button = LabelButton(
            relative={'size': True, 'pos': True},
            pos=[0.95, 0.05],
            size=[0.05, 0.05],
            bg_color=[1, 0, 0, 1],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='X'
        )
        exit_button.on_click = self.remove_info_layout

        info_text = TextInput(
            relative={'pos': True},
            pos=[0.1, 0.2],
            size=[0.8, 0.6],
            font_color=[1, 1, 1, 1],
            font_size=14,
            shadow=True,
            shadow_color=[0, 0.1, 0.1, 1],
            text=display_text
        )

        self.info_layout.add_widget(exit_button)
        self.info_layout.add_widget(info_text)
        self.menu.add_widget(self.info_layout)

    def remove_info_layout(self, *a):
        self.menu.remove_widget(self.info_layout)

    def get_object_info(self, obj):
        obj_info = {
            'name': obj.name,
            'global_position': list(obj.worldPosition),
            'local_position': list(obj.localPosition),
            'global_orientation': list(obj.worldOrientation.to_euler()),
            'local_orientation': list(obj.localOrientation.to_euler()),
            'scale': list(obj.localScale),
            'color': list(obj.color),
            'properties': {prop_name: obj[prop_name] for prop_name in obj.getPropertyNames()},
            'materials': [mat.name for mat in obj.meshes[0].materials] if obj.meshes else [],
        }

        if obj.getPhysicsId():
            obj_info.update({
                'mass': obj.mass,
                'velocity': list(obj.getLinearVelocity()),
            })

        return obj_info

    def quit(self, *a):
        bge.logic.endGame()
    
    def showInfo(self, *a):
        self.info_button.text = "Working"
        self.store_objects_info()

    def edit_object(self, *a):
        print("Edit button clicked")

    def toggle_visibility(self, obj, button, *a):
        obj.visible = not obj.visible
        button.text = 'Show' if obj.visible else 'Hide'

    def update(self):
        if key_press('esc'):
            self.show_menu = not self.show_menu
            self.floating_ui.show = not self.show_menu
            self.mouselook.active = not self.show_menu
            self.menu.show = self.show_menu
            self.cursor.show = self.show_menu
        if self.show_menu:
            pass

        if hasattr(self, 'update_counter'):
            self.update_counter -= 1
            if self.update_counter <= 0:
                self.update_counter = 12  # Update 5 times a second (60 FPS / 5 = 12)
                if hasattr(self, 'current_object'):
                    self.display_object_info(self.current_object)
        else:
            self.update_counter = 12

    def set_menu_false(self, arg):
        self.show_menu = False
        self.floating_ui.show = not self.show_menu
        self.mouselook.active = not self.show_menu
        self.menu.show = self.show_menu
        self.cursor.show = self.show_menu

    def store_objects_info(self):
        scene = bge.logic.getCurrentScene()
        objects_info = []

        for obj in scene.objects:
            obj_info = self.get_object_info(obj)
            objects_info.append(obj_info)

        print(objects_info)
        return objects_info
