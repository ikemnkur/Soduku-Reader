import bge
from collections import OrderedDict
from uplogic.ui import Canvas
from uplogic.ui import RelativeLayout
from uplogic.ui import BoxLayout
from uplogic.ui import LabelButton
from uplogic.ui import Button
from uplogic.ui import Cursor
from uplogic.ui import Image
from uplogic.ui import TextInput
from uplogic.input import MouseLook
from uplogic.input import key_press
from uplogic.decorators import game_props
from uplogic.utils import world_to_screen
from mathutils import Vector


class SearchButton(Button):
    
    def start(self):
        self.bg_color = (0, 0, 0, .5)
        self.text_input = TextInput(
            text='Search',
            valign='center',
            pos=(.05, .5),
            relative={'pos': True}
        )
        self.add_widget(self.text_input)
    
    def on_press(self, widget):
        self.text_input.edit = True

class ModifyProperty(Button):
    
    def start(self):
        self.bg_color = (0, 0, 0, .5)
        self.text_input = TextInput(
            text='Value',
            valign='center',
            halign='center',
            pos=(.05, .5),
            relative={'pos': True}
        )
        self.add_widget(self.text_input)
    
    def on_press(self, widget):
        self.text_input.edit = True

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
        self.floating_ui.add_widget(self.reticle)
        self.floating_ui.add_widget(self.UI_marker)
        self.floating_ui.add_widget(self.suzanne_button)

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

        # Return to game button
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

        # Quit game button
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

        # Info button
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

        # Right window content
        self.right_window = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[.2, 0],
            size=[.8, 1],
            bg_color=[0, 0, .2, 0],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )

        # Text layout for displaying info
        self.right_textLayout = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[.5, .4],
            size=[.8, 0.1],
            bg_color=[0, .6, .2, 0.25],
            border_width=1,
            border_color=[1, 1, 1, 1],
            orientation='vertical'
        )
        
        # Info text input
        self.info_text = SearchButton(size=(1, .5), relative={'size': True})
        
        # Main text input for displaying object info
        self.main_text = TextInput(
            relative={'pos': True},
            pos=[.5, .5],
            font_color=[1, 1, 1, 1],
            font_size=14,
            shadow = True,
            shadow_color=[0, 0.1, 0.1, 1],
            text='Info'
        )

        # Exit menu button
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
        
        # Add all widgets to the menu
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

        # Store information about objects
        self.objects_info = self.store_objects_info()

        # Add UI elements for each game object
        self.add_game_objects_ui()

    def add_game_objects_ui(self):
        """Add UI elements for each game object"""
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
        """Display the selected object's info in a new layout, hiding the object names layout"""
        obj_info = self.get_object_info(obj)

        # Hide the object names layout
        self.right_window.show = False

        # Create the new layout for object info
        self.info_layout = BoxLayout(
            relative={'pos': True, 'size': True},
            pos=[0.275, -0.2],
            size=[0.6, 1],
            bg_color=[0, 0, 0, 0],
            orientation='vertical'
        )

        # Back button to return to the object names layout
        back_button = LabelButton(
            relative={'size': True, 'pos': True},
            pos=[0.9, 0.9],
            size=[0.1, 0.05],
            bg_color=[1, 0, 0, 1],
            border_width=1,
            border_color=[1, 1, 1, 1],
            text='BACK'
        )
        back_button.on_click = self.show_object_names_layout

        # Display object properties and attributes as LabelButtons with "Change" button
        for key, value in obj_info.items():
            property_layout = BoxLayout(
                relative={'pos': True, 'size': True},
                pos=[0, 0],
                size=[1, .05],
                bg_color=[0, 0, 0, 0],
                orientation='horizontal'
            )

            property_label = LabelButton(
                relative={'size': True, 'pos': True},
                pos=[0, 0],
                size=[.25, 1],
                bg_color=[0, 0, 0, 0],
                border_width=1,
                border_color=[1, 1, 1, 1],
                text=f"{key}:"
            )

            class ModProps(Button):
    
                def start(self):
                    self.bg_color = (0, 0, 0, .5)
                    self.text_input = TextInput(
                        text=f'{value}',
                        valign='center',
                        halign='center',
                        pos=(0.5, 0.5),
                        # bg_color=[0, 0, 0, 0],
                        # border_width=1,
                        # border_color=[1, 1, 1, 1],
                        relative={'pos': True}
                    )
                    self.add_widget(self.text_input)
                
                def on_press(self, widget):
                    self.text_input.edit = True

            property_value = ModProps(size=(0.65, 1), relative={'size': True})

            change_button = LabelButton(
                relative={'size': True, 'pos': True},
                pos=[.8, 0],
                size=[.1, 1],
                bg_color=[0, 0, 0, 0],
                border_width=1,
                border_color=[1, 1, 1, 1],
                text='Change'
            )
            change_button.on_click = lambda *a, key=key: self.change_property(obj, key)

            property_layout.add_widget(property_label)
            property_layout.add_widget(property_value)
            property_layout.add_widget(change_button)

            self.info_layout.add_widget(property_layout)

        self.info_layout.add_widget(back_button)
        self.menu.add_widget(self.info_layout)

    def show_object_names_layout(self, *a):
        """Show the object names layout and hide the object info layout"""
        self.menu.remove_widget(self.info_layout)
        self.right_window.show = True

    def change_property(self, obj, key):
        """Handler for the 'Change' button to modify object properties"""
        print(f"Change property '{key}' of object '{obj.name}'")

    def get_object_info(self, obj):
        """Retrieve information about the selected object"""
        obj_info = {
            'name': obj.name,
            # 'global_position': list(obj.worldPosition),
            'global_position': [round(val, 2) for val in obj.worldPosition],
            # 'local_position': list(obj.localPosition),
            'local_position': [round(val, 2) for val in obj.localPosition],
            # 'global_orientation': list(obj.worldOrientation.to_euler()),
            'global_orientation': [round(val, 2) for val in obj.worldOrientation.to_euler()],
            # 'local_orientation': list(obj.localOrientation.to_euler()),
            'local_orientation': [round(val, 2) for val in obj.localOrientation.to_euler()],
            # 'scale': list(obj.localScale),
            'scale': [round(val, 2) for val in obj.localScale],
            'color': list(obj.color),
            'properties': {prop_name: obj[prop_name] for prop_name in obj.getPropertyNames()},
            'materials': [mat.name for mat in obj.meshes[0].materials] if obj.meshes else [],
        }

        # Additional attributes for dynamic objects
        if obj.getPhysicsId():
            obj_info.update({
                'mass': obj.mass,
                # 'velocity': list(obj.getLinearVelocity()),
                'velocity': [round(val, 2) for val in obj.getLinearVelocity()],
            })
            print('lol')

        return obj_info

    def quit(self, *a):
        """End the game"""
        bge.logic.endGame()
    
    def showInfo(self, *a):
        """Show information button handler"""
        self.info_button.text = "Working"
        self.store_objects_info()

    def edit_object(self, *a):
        """Edit button handler"""
        print("Edit button clicked")

    def toggle_visibility(self, obj, button, *a):
        """Toggle the visibility of the selected object"""
        obj.visible = not obj.visible
        button.text = 'Show' if obj.visible else 'Hide'

    def update(self):
        """Update method called every frame"""
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
        
#        self.display_object_info(self.current_object)
        

        # Update displayed object info periodically
        if hasattr(self, 'update_counter'):
            self.update_counter -= 1
            print(self.update_counter)
            if self.update_counter <= 0:
                self.update_counter = 12  # Update 5 times a second (60 FPS / 5 = 12)
                if hasattr(self, 'current_object'):
                    self.display_object_info(self.current_object)
                    print("updated info")
        else:
            self.update_counter = 12
            print("Update counter initialized")

    def rotate_suzanne(self, *a):
        self.object.scene.objects['Suzanne.001'].applyRotation((0, 0, 3.1516 * .25))


    def set_menu_false(self, arg):
        """Set the menu visibility to false"""
        self.show_menu = False
        self.floating_ui.show = not self.show_menu
        self.mouselook.active = not self.show_menu
        self.menu.show = self.show_menu
        self.cursor.show = self.show_menu

    def store_objects_info(self):
        """Store information about all objects in the scene"""
        scene = bge.logic.getCurrentScene()
        objects_info = []

        for obj in scene.objects:
            obj_info = self.get_object_info(obj)
            objects_info.append(obj_info)

#        print(objects_info)
        return objects_info
