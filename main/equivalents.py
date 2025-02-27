import os
import json
from PIL import ImageTk, Image
import tkinter as tk
from tkinter.messagebox import showinfo, showwarning
from tkinter.filedialog import askopenfilename
from tkinter import ttk

# Read the data from library.json
with open(os.path.join(os.path.dirname(__file__),'library.json'), 'r', encoding='utf-8') as file:
    data = json.load(file)

class CalculatorModel:
    def __init__(self):
        pass

    def to_mols(self, name: str, init_amount: float) -> float:
        """Calculates the number of moles for a reagent.
        
        Parameters
        ----------
        name : str
            The name of the reagent.

        init_amount : float
            The initial amount of the reagent (mL for liquids and solutions or g for solids).
        
        Returns
        -------
        float	
            Number of moles of the chemical substance (mol).
        """

        for reagent in data:
            if reagent['name'] == name:
                category = reagent['category']
                if category == 'solid':
                    return init_amount/reagent['molar mass']
                elif category == 'liquid':
                    return reagent['density']*init_amount/reagent['molar mass']
                elif category == 'percent solution':
                    return reagent['solution concentration']*reagent['solution density']*init_amount/(100*reagent['molar mass'])
                elif category == 'molar solution':
                    return init_amount*reagent['solution concentration']/1000
    
    def from_mols(self, name: str, init_amount: float) -> float:
        """Calculates the mass or volume of a reagent.
        
        Parameters
        ----------
        name : str
            The name of the reagent.

        init_amount : float
            The initial number of moles of the chemical substance (mol).
        
        Returns
        -------
        float	
            Necessary mass (g) or volume (mL) of the reagent.
        """

        for reagent in data:
            if reagent['name'] == name:
                category = reagent['category']
                if category == 'solid':
                    return reagent['molar mass']*init_amount
                elif category == 'liquid':
                    return reagent['molar mass']*init_amount/reagent['density']
                elif category == 'percent solution':
                    return reagent['molar mass']*init_amount*100/(reagent['solution density']*reagent['solution concentration'])
                elif category == 'molar solution':
                    return init_amount*1000/reagent['solution concentration']

class CalculatorFrame(tk.Frame):
    def __init__(self, parent, controller):
        self.bg_color = 'bisque1'
        super().__init__(parent, bg=self.bg_color)
        self.pack(fill='both', expand=True, padx=10, pady=5)

        # Set a controller
        self.controller = controller

        # Create frame with radiobuttons
        frame_radio = tk.Frame(self, bg=self.bg_color)
        tk.Label(frame_radio, text='Select number of reagents:', bg=self.bg_color).grid(row=0, column=0)
        
        list=['2 reagents', '3 reagents', '4 reagents', '5 reagents']
        for i in range(4):
            radiobtn = tk.Radiobutton(
                frame_radio,
                variable=self.controller.num_of_reagents,
                value=i+2,
                text=list[i], 
                bg=self.bg_color,
                activebackground=self.bg_color,
                command=self.controller.update_view
                )
            radiobtn.grid(row=0, column=i+1)

        frame_radio.pack(fill='both', expand=True, padx=10, pady=5)

        # Store combobox variables and corresponding labels and entries
        self.reagent_vars = {}  
        self.reagent_labels = {}
        self.reagent_entries = {} 
               
        # Create reaction scheme       
        self.frame_scheme = tk.Frame(self, bg='white', borderwidth=2, relief='ridge')       
        self.create_reaction_scheme(self.frame_scheme)
        self.frame_scheme.pack(fill='both', expand=True, padx=10, pady=5)

        # Create results frame
        frame_results = tk.LabelFrame(self, text='Results', bg=self.bg_color)
        
        self.results_label = tk.Label(frame_results, text='', bg=self.bg_color)
        self.results_label.pack()

        frame_results.pack(fill='both', expand=True, padx=10, pady=5)

        # Create button
        tk.Button(self, text='Calculate', bg='beige', activebackground='beige', command=self.controller.calculate_button_clicked).pack(pady=5)

    def create_reaction_scheme(self, frame):
        """Creates alternating FrameTypeA and FrameTypeB, ending with "-->products"."""

        # Clear existing widgets
        for widget in frame.winfo_children():
            widget.destroy()
        
        self.reagent_vars.clear()
        self.reagent_labels.clear()
        self.reagent_entries.clear()

        num_of_reagents = self.controller.num_of_reagents.get()
        labels = [f'A (limiting reagent)', 'B', 'C', 'D', 'E']

        for i in range(num_of_reagents):
            reagent_var = tk.StringVar()  # Create an independent variable for each combobox
            self.reagent_vars[i] = reagent_var  # Store in dictionary
            label_text = labels[i]
            
            if i == 0:
                unit = ''
                first=True
                self.create_frame_type_A(frame, label_text, unit, i, reagent_var, first).pack(side=tk.LEFT)
            else:
                unit = 'eq'
                first = False
                self.create_frame_type_A(frame, label_text, unit, i, reagent_var, first).pack(side=tk.LEFT)
        
            # Add FrameTypeB only if it's NOT the last iteration
            if i < num_of_reagents - 1:
                self.create_frame_type_B(frame).pack(side=tk.LEFT)

        # Add the final "-->products" label instead of "+"
        tk.Label(frame, text='--> products', bg='white').pack(side=tk.LEFT)
    
    def create_frame_type_A(self, frm, label_text, unit, index, reagent_var, first=False):
        """Creates a FrameTypeA containing a Combobox, Label, and Entry (with unit 'g')."""

        frame = tk.Frame(frm, bg='white')

        reagent_combobox = ttk.Combobox(frame, background='white', values=[item['name'] for item in data], textvariable=reagent_var, state='readonly')
        reagent_combobox.pack(padx=5, pady=5)
        reagent_combobox.bind('<<ComboboxSelected>>', lambda event, idx=index: self.controller.display_image(event, idx))

        reagent_label = tk.Label(frame, text=label_text, bg='white')
        reagent_label.pack()

        # Store label reference
        self.reagent_labels[index] = reagent_label 

        # Frame to hold entry and unit label
        entry_frame = tk.Frame(frame, bg='white')

        entry = tk.Entry(entry_frame, width=5, bg='white')
        entry.pack(side=tk.LEFT)

        # Store entry reference
        self.reagent_entries[index] = entry

        label_unit = tk.Label(entry_frame, bg='white', text=unit)
        label_unit.pack(side=tk.LEFT)
    
        entry_frame.pack(padx=5, pady=5)

        # If it's the first frame, bind the combobox to update the unit dynamically
        if first:
            reagent_combobox.bind('<<ComboboxSelected>>', lambda event, name=reagent_var, lbl=label_unit: self.controller.update_unit_label(event, name, lbl), add='+')

        return frame
    
    def create_frame_type_B(self, frm):
        """Creates a FrameB containing the "+" sign."""

        frame = tk.Frame(frm, bg='white')

        tk.Label(frame, text='+', bg='white').pack()

        return frame

class CalculatorController:
    def __init__(self, parent):
        self.parent = parent
        self.num_of_reagents = tk.IntVar(value=2)
        self.first_label_unit = None

        # Create model and frame
        self.model = CalculatorModel()
        self.frame = CalculatorFrame(self.parent, self)  
    
    def update_view(self):
        "Updates the reaction scheme and the results frame according to the radiobutton selected."
        self.frame.create_reaction_scheme(self.frame.frame_scheme)
        self.frame.results_label.config(text='')
    
    def resize_image(self, image_path, new_height):
        original_image = Image.open(image_path)
    
        # Calculate the new width to maintain the aspect ratio
        aspect_ratio = original_image.width / original_image.height
        new_width = int(new_height * aspect_ratio)
    
        # Resize the image
        resized_image = original_image.resize((new_width, new_height))
    
        return resized_image

    def display_image(self, event, index):
        """Changes the reagent label in reaction scheme to an image corresponding to the reagent selected in reagent combobox."""

        # Get the name from combobox
        name = self.frame.reagent_vars[index].get()

        # Find the corresponding image
        image = [reagent['image'] for reagent in data if reagent['name'] == name]

        if not image:  # If no image is found, return early
            return  

        image_path = os.path.abspath(os.path.join(os.path.join(os.path.join(os.path.dirname(__file__),'..'),'images'), image[0]))

        # Create image and convert for Tkinter
        img = self.resize_image(image_path, new_height=80)
        img = ImageTk.PhotoImage(img)

        # Configure the label with the image
        self.frame.reagent_labels[index].config(image=img, text='') # Clear text when setting an image
        self.frame.reagent_labels[index].image = img # Keep a reference to the image

    def update_unit_label(self, event, reagent_var, label_unit):
        """Updates the unit label based on the selected reagent (g for solids, mL for liquids/solutions)."""
        selected_reagent = reagent_var.get()

        for reagent in data:
            if reagent['name'] == selected_reagent:
                category = reagent['category']
                new_unit = 'g' if category == 'solid' else 'mL'
                label_unit.config(text=new_unit)
                self.first_label_unit = label_unit.cget('text')
                break

    def calculate_button_clicked(self):
        '''Modifies the label in results frame displaying calculation results.'''
        try:
            # First reagent
            name_of_A = self.frame.reagent_vars[0].get()
            unit_of_A = self.first_label_unit
            inital_amount_of_A = float(self.frame.reagent_entries[0].get())
            num_of_moles_of_A = self.model.to_mols(name_of_A, inital_amount_of_A)

            num_of_reagents = self.num_of_reagents.get()

            # Other reagents
            results = []
            for i in range(num_of_reagents):
                if not i == 0:
                    name_of_reagent = self.frame.reagent_vars[i].get()
                    for reagent in data:
                        if reagent['name'] == name_of_reagent:
                            category = reagent['category']
                            if category == 'solid':
                                unit='g'
                            else:
                                unit='mL'
                    eqs = float(self.frame.reagent_entries[i].get())
                    num_of_moles = num_of_moles_of_A * eqs
                    result = round(self.model.from_mols(name_of_reagent, num_of_moles), 2)
                    result = f'\n{result} {unit} of {name_of_reagent} ({eqs} eq)'
                    results.append(result)

            # Update the label in results frame
            self.frame.results_label.configure(text=f'For {inital_amount_of_A} {unit_of_A} of {name_of_A}, measure:\n{''.join(results)}')

        except ValueError:
            showwarning(title='Warning!', message='Check input values!')
        except TypeError:
            showwarning(title='Warning!', message='Select reagents!')
        
class AddToDatabaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        self.bg_color = 'bisque1'
        super().__init__(parent, bg=self.bg_color)
        self.pack(fill='both', expand=True, padx=10, pady=5)

        # Set a controller
        self.controller = controller

        # Fix the first column's width
        self.grid_columnconfigure(0, minsize=200)

        self.create_widgets()

    def create_widgets(self):
        """Creates widgets based on the category selection."""

        # Preserve name entry value if not empty
        name_value = self.name_entry.get() if hasattr(self, 'name_entry') and self.name_entry.get().strip() else ''

        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Name
        tk.Label(self, text='Name:', bg=self.bg_color).grid(row=0, column=0)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1)

        # Category
        tk.Label(self, text='Category:', bg=self.bg_color).grid(row=1, column=0)

        category_combobox = ttk.Combobox(self, textvariable=self.controller.category_var,
                                              values=['solid', 'liquid', 'percent solution', 'molar solution'],
                                              state='readonly', width=17, background=self.bg_color)
        category_combobox.grid(row=1,column=1)                    
        category_combobox.bind('<<ComboboxSelected>>', self.controller.update_view)

        # Molar Mass
        tk.Label(self, text='Molar Mass [g/mol]:', bg=self.bg_color).grid(row=2, column=0)
        self.molar_mass_entry = tk.Entry(self)
        self.molar_mass_entry.grid(row=2, column=1)

        # Image Filename
        tk.Button(self, text='Select Image', bg='beige', activebackground='beige', command=self.controller.add_image_path).grid(row=5, column=0)
        self.image_label = tk.Label(self, text='No image selected...', bg=self.bg_color)
        self.image_label.grid(row=5, column=1)

        # Submit Button
        self.submit_button = tk.Button(self, text='Add Reagent', bg='beige', activebackground='beige', command=self.controller.add_reagent)
        self.submit_button.grid(row=6, columnspan=2, pady=5)

        # Restore name entry value if not empty
        if name_value:
            self.name_entry.insert(0, name_value)

class AddToDatabaseController:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent 
        self.bg_color = 'bisque1'
        self.category_var = tk.StringVar(value='solid')

        # Create the frame
        self.frame = AddToDatabaseFrame(self.parent, self)
        
    def update_view(self, event):
        """Updates the frame according to the category selected."""

        category = self.category_var.get()

        self.frame.create_widgets()

        if category == 'liquid':
            tk.Label(self.frame, text='Density [g/mL]:', bg=self.bg_color).grid(row=3, column=0)
            self.density_entry = tk.Entry(self.frame)
            self.density_entry.grid(row=3, column=1)
        elif category == 'percent solution':
            tk.Label(self.frame, text='Solution Concentration [%]:', bg=self.bg_color).grid(row=3, column=0)
            self.percent_conc_entry = tk.Entry(self.frame)
            self.percent_conc_entry.grid(row=3, column=1)

            tk.Label(self.frame, text='Solution Density [g/mL]:', bg=self.bg_color).grid(row=4, column=0)
            self.sol_density_entry = tk.Entry(self.frame)
            self.sol_density_entry.grid(row=4, column=1)
        elif category == 'molar solution':
            tk.Label(self.frame, text='Solution Concentration [mol/L]:', bg=self.bg_color).grid(row=3, column=0)
            self.molar_conc_entry = tk.Entry(self.frame)
            self.molar_conc_entry.grid(row=3, column=1)  
    
    def add_image_path(self):
        initial_dir = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__),'..'),'images'))
        image_path = askopenfilename(initialdir=initial_dir)
        if image_path:  # If a file is selected, update the entry widget
            image = os.path.basename(image_path)
            self.frame.image_label.config(text=image)

    def add_reagent(self):
        """Collects input and adds to database."""

        try:
            reagent = {
                'name': self.frame.name_entry.get(),
                'category': self.category_var.get(),
                'molar mass': float(self.frame.molar_mass_entry.get())
            }

            # Add additional properties based on category
            if reagent['category'] == 'liquid':
                reagent['density'] = float(self.density_entry.get())
            elif reagent['category'] == 'percent solution':
                reagent['solution concentration'] = float(self.percent_conc_entry.get())
                reagent['solution density'] = float(self.sol_density_entry.get())
            elif reagent['category'] == 'molar solution':
                reagent['solution concentration'] = float(self.molar_conc_entry.get())  

            if not self.frame.image_label.cget('text') == 'No image selected...':
                reagent['image'] = self.frame.image_label.cget('text')
            else:
                reagent['image'] = ''

            path_to_library = os.path.join(os.path.dirname(__file__),'library.json')

            # Update the database
            global data
            data.append(reagent)
            with open(path_to_library, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2)

            # Clear the input values
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
            self.frame.image_label.config(text='No image selected...')
            
            # Update view in Tab1
            self.app.update_view()
            
            showinfo(title='Success!', message='The reagent was added to the database!')
        
        except ValueError:
            showwarning(title='Warning!', message='Check the input values!')

class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title('Equivalents Calculator')
        self.resizable(0, 0)

        # Create Tabs
        self.notebook = ttk.Notebook(self)  
        self.tab1 = tk.Frame(self.notebook, bg='bisque1')
        self.tab2 = tk.Frame(self.notebook, bg='bisque1')
        self.notebook.add(self.tab1, text='calculate equivalents')
        self.notebook.add(self.tab2, text='add reagents to database')
        self.notebook.pack(fill='both', expand=True)

        # Create controllers
        self.calculator_controller = CalculatorController(self.tab1)
        AddToDatabaseController(self, self.tab2)

    def update_view(self):
        """Updates the view in Tab1 after a new reagent was added in Tab2. This ensures the new reagent is immediately accessible for calculations in Tab1."""

        self.calculator_controller.update_view()

if __name__ == '__main__':
    # Run the application
    App = CalculatorApp()
    App.mainloop()