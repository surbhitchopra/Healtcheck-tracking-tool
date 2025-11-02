import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
import re
from collections import defaultdict

class CustomerNetworkSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Customer & Network Selection")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.selected_customer = tk.StringVar()
        self.selected_network = tk.StringVar()
        self.customer_networks = defaultdict(list)
        self.result = None
        
        # Load available customers and networks
        self.load_customers_and_networks()
        
        # Create GUI
        self.create_gui()
        
    def load_customers_and_networks(self):
        """Load all available customers and their networks from HC tracker files"""
        script_dir = Path(__file__).parent
        
        # Look for HC tracker files in current directory and subdirectories
        tracker_files = []
        
        # Search in Script directory
        for file_path in script_dir.glob("*_HC_Issues_Tracker.xlsx"):
            if not file_path.name.startswith("Template_"):
                tracker_files.append(file_path.name)
        
        # Search in customer_files subdirectories
        customer_files_dir = script_dir / "customer_files"
        if customer_files_dir.exists():
            for file_path in customer_files_dir.rglob("*_HC_Issues_Tracker.xlsx"):
                if not file_path.name.startswith("Template_"):
                    tracker_files.append(file_path.name)
        
        # Parse customer and network names
        for tracker_file in tracker_files:
            # Remove "_HC_Issues_Tracker.xlsx" from filename
            network_name = tracker_file.replace("_HC_Issues_Tracker.xlsx", "")
            
            # Extract customer name (everything before the first zone/region identifier)
            customer = self.extract_customer_name(network_name)
            
            # Add to customer_networks dictionary
            if customer and network_name:
                self.customer_networks[customer].append(network_name)
        
        # Sort networks for each customer
        for customer in self.customer_networks:
            self.customer_networks[customer].sort()
    
    def extract_customer_name(self, network_name):
        """Extract customer name from network name"""
        network_lower = network_name.lower()
        
        # Define customer patterns
        if 'bsnl' in network_lower:
            return 'BSNL'
        elif 'airtel' in network_lower:
            return 'Airtel'
        elif 'reliance' in network_lower:
            return 'Reliance'
        elif 'railtel' in network_lower:
            return 'RailTel'
        elif 'timedotcom' in network_lower:
            return 'TimeDotCom'
        elif 'vodafone' in network_lower:
            return 'Vodafone'
        elif 'idea' in network_lower:
            return 'Idea'
        elif 'jio' in network_lower:
            return 'Jio'
        else:
            # For unknown patterns, use the first part as customer name
            parts = network_name.split('_')
            if parts:
                return parts[0].title()
        
        return None
    
    def create_gui(self):
        """Create the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Select Customer and Network", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Customer selection
        ttk.Label(main_frame, text="Customer:", font=('Arial', 12)).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.customer_combo = ttk.Combobox(main_frame, textvariable=self.selected_customer,
                                          font=('Arial', 11), width=30)
        self.customer_combo['values'] = sorted(list(self.customer_networks.keys()))
        self.customer_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_selected)
        
        # Network selection
        ttk.Label(main_frame, text="Network:", font=('Arial', 12)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.network_combo = ttk.Combobox(main_frame, textvariable=self.selected_network,
                                         font=('Arial', 11), width=30)
        self.network_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        self.network_combo.state(['disabled'])  # Initially disabled
        
        # Info text
        info_text = """Instructions:
1. Select a customer from the dropdown above
2. Select the specific network for that customer
3. Click 'Proceed' to continue with HC processing"""
        
        info_label = ttk.Label(main_frame, text=info_text, font=('Arial', 10),
                              foreground='blue', justify=tk.LEFT)
        info_label.grid(row=3, column=0, columnspan=2, pady=(20, 20), sticky=tk.W)
        
        # Available networks display
        ttk.Label(main_frame, text="Available Networks:", font=('Arial', 12, 'bold')).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Listbox for showing networks
        self.network_listbox = tk.Listbox(main_frame, height=8, font=('Arial', 10))
        self.network_listbox.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.network_listbox.yview)
        scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.network_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Configure row weight for listbox expansion
        main_frame.rowconfigure(5, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Buttons
        ttk.Button(button_frame, text="Proceed", command=self.proceed,
                  width=15).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel,
                  width=15).grid(row=0, column=1)
        
        # Initially show all networks
        self.update_network_display()
    
    def on_customer_selected(self, event=None):
        """Handle customer selection"""
        customer = self.selected_customer.get()
        if customer and customer in self.customer_networks:
            # Enable network combobox
            self.network_combo.state(['!disabled'])
            
            # Update network combobox values
            networks = self.customer_networks[customer]
            self.network_combo['values'] = networks
            
            # Clear previous selection
            self.selected_network.set('')
            
            # If only one network, auto-select it
            if len(networks) == 1:
                self.selected_network.set(networks[0])
            
            # Update network display
            self.update_network_display(customer)
    
    def update_network_display(self, selected_customer=None):
        """Update the network display listbox"""
        self.network_listbox.delete(0, tk.END)
        
        if selected_customer and selected_customer in self.customer_networks:
            # Show networks for selected customer
            networks = self.customer_networks[selected_customer]
            self.network_listbox.insert(tk.END, f"Networks for {selected_customer}:")
            self.network_listbox.insert(tk.END, "-" * 40)
            for network in networks:
                self.network_listbox.insert(tk.END, f"  • {network}")
        else:
            # Show all customers and their network counts
            self.network_listbox.insert(tk.END, "Available Customers:")
            self.network_listbox.insert(tk.END, "-" * 40)
            for customer, networks in sorted(self.customer_networks.items()):
                self.network_listbox.insert(tk.END, f"  • {customer} ({len(networks)} networks)")
    
    def proceed(self):
        """Handle proceed button click"""
        customer = self.selected_customer.get()
        network = self.selected_network.get()
        
        if not customer:
            messagebox.showwarning("Selection Required", "Please select a customer.")
            return
        
        if not network:
            messagebox.showwarning("Selection Required", "Please select a network.")
            return
        
        # Store the result
        self.result = {
            'customer': customer,
            'network': network
        }
        
        # Show confirmation
        messagebox.showinfo("Selection Confirmed", 
                           f"Selected:\nCustomer: {customer}\nNetwork: {network}")
        
        # Close the window
        self.root.quit()
        self.root.destroy()
    
    def cancel(self):
        """Handle cancel button click"""
        self.result = None
        self.root.quit()
        self.root.destroy()
    
    def show(self):
        """Show the dialog and return the selected customer and network"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Show the window
        self.root.mainloop()
        
        return self.result

def select_customer_and_network():
    """Function to show the customer and network selection dialog"""
    selector = CustomerNetworkSelector()
    return selector.show()

if __name__ == "__main__":
    # Test the selector
    result = select_customer_and_network()
    if result:
        print(f"Selected Customer: {result['customer']}")
        print(f"Selected Network: {result['network']}")
    else:
        print("No selection made or cancelled")
