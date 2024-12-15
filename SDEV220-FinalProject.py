import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from tkinter import simpledialog
from datetime import datetime





# Connect to SQLite database
conn = sqlite3.connect('appointments.db')
cursor = conn.cursor()

# Create the appointments table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS appointments
                  (id INTEGER PRIMARY KEY, customer_name TEXT, phone_number TEXT, 
                   date TEXT, time TEXT, service TEXT, comments TEXT)''')
conn.commit()

# Function to save appointments (handled by SQLite automatically)
def save_appointments():
    conn.commit()

def main_window():
    # Main window setup
    def show_login():
        # Hide the main buttons and show the login form
        button_staff.pack_forget()
        login_frame.pack(pady=20)

    def login(event=None):
        username = entry_username.get()
        password = entry_password.get()

        # Here we're using hardcoded login credentials for simplicity
        if username == "123" and password == "123":
            
            # Hide the login form
            login_frame.pack_forget()
            
            # Show the appointments view
            view_appointments()

        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")


    def book_appointment_window():
        def fetch_availability(selected_date):
            # Predefined working hours (9:00 AM to 4:00 PM)
            all_slots = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"]
            
            # Query booked slots for the selected date
            cursor.execute("SELECT time FROM appointments WHERE date = ?", (selected_date,))
            booked_times = [row[0] for row in cursor.fetchall()]
            
            # Determine available slots
            available_slots = [slot for slot in all_slots if slot not in booked_times]
            return available_slots

        def update_time_dropdown(event):
            # Get the selected date from the calendar
            selected_date = cal.get_date()

            
            if selected_date:
                # Fetch available slots for the selected date
                available_slots = fetch_availability(selected_date)

                # Update the dropdown with available slots
                time_var.set("")  # Clear current selection
                time_dropdown['values'] = available_slots

        # Create a new window for booking
        book_win = tk.Toplevel(root)
        book_win.title("Book Appointment")
        book_win.geometry("400x900")
        book_win.configure(bg="white")

        # Calendar for selecting a date
        tk.Label(book_win, text="Select Date:", bg="white").pack(pady=5)
        cal = Calendar(book_win, date_pattern="yyyy-mm-dd", background="grey", foreground="black", borderwidth=2)
        cal.pack(pady=10)
        

        # Bind date selection to update the time dropdown
        cal.bind("<<CalendarSelected>>", update_time_dropdown)

        # Dropdown for available time slots
        tk.Label(book_win, text="Select Time:", bg="white").pack(pady=5)
        time_var = tk.StringVar()
        time_dropdown = ttk.Combobox(book_win, textvariable=time_var, state="readonly")
        time_dropdown.pack(pady=5)

        # Services with checkboxes
        tk.Label(book_win, text="Select Services:", bg="white").pack(pady=5)
        services = ["Haircut", "Bath", "Hair Coloring", "Nail Trim", "Deshed", "Glands", "Other, specify"]
        selected_services = {service: tk.IntVar() for service in services}

        for service, var in selected_services.items():
            tk.Checkbutton(book_win, text=service, variable=var, bg="white").pack(anchor="w", padx=20)

        # User details
        tk.Label(book_win, text="Your Name:", bg="white").pack(pady=5)
        name_entry = tk.Entry(book_win)
        name_entry.pack(pady=5)

        tk.Label(book_win, text="Your Phone Number:", bg="white").pack(pady=5)
        phone_entry = tk.Entry(book_win)
        phone_entry.pack(pady=5)

        tk.Label(book_win, text="Comments:", bg="white").pack(pady=5)
        comments_entry = tk.Entry(book_win)
        comments_entry.pack(pady=5)

        def submit_appointment():
            selected_date = cal.get_date()
            selected_time = time_var.get()
            name = name_entry.get()
            phone = phone_entry.get()
            comments = comments_entry.get()

            if not selected_date or not selected_time or not name or not phone:
                messagebox.showerror("Error", "All fields must be filled out.")
                return

            # Get the selected services
            selected_services_list = [service for service, var in selected_services.items() if var.get() == 1]
            services = ", ".join(selected_services_list)  # Join the selected services into a comma-separated string

            # Insert the appointment into the database
            cursor.execute("INSERT INTO appointments (date, time, service, customer_name, phone_number, comments) VALUES (?, ?, ?, ?, ?, ?)",
                        (selected_date, selected_time, services, name, phone, comments))
            conn.commit()
            messagebox.showinfo("Success", "Booked successfully! We will call to confirm appointment.")
            book_win.destroy()

        # Submit button
        submit_button = tk.Button(book_win, text="Book Appointment", command=submit_appointment, bg="light blue")
        submit_button.pack(pady=10)

        # Back button to return to main window
        back_button = tk.Button(book_win, text="Back", bg="light blue", command=lambda: [book_win.destroy(), button_staff.pack(pady=20)])
        back_button.pack(pady=10)

    def delete_appointment(listbox, appointments, view_win):
        selected_index = listbox.curselection()
        if selected_index:
            selected_appointment = appointments[selected_index[0]]
            appointment_id = selected_appointment[0]  # assuming the first column is the ID

            # Confirmation dialog to ask if the user is sure
            confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this appointment?")
            if confirmation:
                # Delete the appointment from the database
                cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
                conn.commit()

                # Remove the appointment from the listbox
                listbox.delete(selected_index)

                # Remove from the local appointments list
                appointments.pop(selected_index[0])

                # Optional: Provide feedback about the successful deletion
                messagebox.showinfo("Success", "Appointment deleted successfully!")

                # Ensure the appointments window stays focused
                view_win.destory()
            else:
                messagebox.showinfo("Cancelled", "Appointment deletion cancelled.")
        else:
            messagebox.showwarning("No Selection", "Please select an appointment to delete.")


    
    def on_close(view_win):
    # Re-show the button after closing the appointments window
        button_staff.pack(pady=20)
        view_win.destroy()

    def view_appointments():
        # Query to fetch appointments
        cursor.execute("SELECT * FROM appointments ORDER BY date ASC")
        appointments = cursor.fetchall()

        # Create a new window to view appointments
        view_win = tk.Toplevel(root)
        view_win.title("Appointments")
        view_win.geometry("700x800")
        view_win.configure(bg="white")

        view_win.transient(root)
        view_win.grab_set()
        view_win.focus_set()

        # Create a frame to hold the listbox and scrollbar
        frame = tk.Frame(view_win)
        frame.pack(pady=10)
        frame.configure(bg="white")

        # Label and listbox for Upcoming Appointments
        tk.Label(frame, text="Upcoming Appointments",bg="white", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, padx=10, pady=(0, 5))  # Label above listbox
        listbox_date = tk.Listbox(frame, height=10, width=50, bg="white")
        listbox_date.grid(row=1, column=0, padx=(10, 20))  # Listbox below the label

        # Add scrollbar for listbox_date
        scrollbar_date = tk.Scrollbar(frame, orient="vertical", command=listbox_date.yview)
        scrollbar_date.grid(row=1, column=1, sticky="ns")  # Place scrollbar next to listbox_date
        listbox_date.config(yscrollcommand=scrollbar_date.set)

        # Populate the listbox with appointments
        for i, appt in enumerate(appointments):
            listbox_date.insert(i, f"{appt[3]} {appt[2]} - {appt[1]}")


        

        # Instruction label at the bottom
        instruction_label = tk.Label(view_win, text="Click on an upcoming appointment to:", bg="white", font=('Helvetica', 10, 'italic'))
        instruction_label.pack(pady=5)


        # Button to view more details of selected appointment
        def show_details():
            selected_index = listbox_date.curselection()
            if selected_index:
                selected_appointment = appointments[selected_index[0]]
                # Display detailed information in a new window
                detail_window = tk.Toplevel(view_win)
                detail_window.title("Appointment Details")
                detail_window.geometry("400x400")
                detail_window.configure(bg="white")

                details = (
                    f"Customer Name: {selected_appointment[1]}\n"
                    f"Phone Number: {selected_appointment[6]}\n"
                    f"Date: {selected_appointment[2]}\n"
                    f"Time: {selected_appointment[3]}\n"
                    f"Service: {selected_appointment[4]}\n"
                    f"Comments: {selected_appointment[5]}"
                )
                tk.Label(detail_window, text=details, bg= "white", justify="left", anchor="w").pack(pady=10)

                tk.Button(detail_window, text="Close",bg="light blue", command=detail_window.destroy).pack(pady=10)

        # Button to show more details
        tk.Button(view_win, text="View Full Details", bg="light blue", command=show_details).pack(pady=10)

        tk.Button(view_win, text="Delete Appointment", bg="light blue", command=lambda: delete_appointment(listbox_date, appointments, view_win)).pack(pady=10)

        # Back button to return to main window
        back_button = tk.Button(view_win, text="Back", bg="light blue", command=lambda: [view_win.destroy(), button_staff.pack(pady=20)])
        back_button.pack(pady=10)

        view_win.protocol("WM_DELETE_WINDOW", lambda: on_close(view_win))

        

    # Main window setup
    root = tk.Tk()
    root.title("Pet Parlor Appointment Scheduler")
    root.geometry("400x400")
    root.configure(bg="white")

    tk.Label(root, text="Welcome to the Pet Parlor", font=("Helvetica", 16, "bold", ), fg= "light blue", bg="white").pack(pady=10, side="top")

    # Book appointment button
    button_customer = tk.Button(root, text="Book Appointment", bg="light blue", width=20, command=book_appointment_window)
    button_customer.pack(pady=20)

    # Staff login button (for viewing appointments)
    button_staff = tk.Button(root, text="Staff Login",bg="light blue", width=20, command=show_login)
    button_staff.pack(pady=20)
    


    # Login form (hidden initially)
    login_frame = tk.Frame(root)
    login_frame.configure(bg="white")

    tk.Label(login_frame, text="Username:", bg="white").pack(pady=5)
    entry_username = tk.Entry(login_frame)
    entry_username.pack(pady=5)

    tk.Label(login_frame, text="Password:", bg="white").pack(pady=5)
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.pack(pady=5)

    root.bind("<Return>", login)

    login_button = tk.Button(login_frame, text="Login", bg="light blue", command=login)
    login_button.pack(pady=10)
    
    

    root.mainloop()

# Run the main window
main_window()

# Close the SQLite connection when done
conn.close()
