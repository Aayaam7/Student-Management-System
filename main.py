


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv
import json
import os

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        
        self.init_database()

        
        self.create_widgets()

        
        self.refresh_student_list()

    def init_database(self):
        """Initialize SQLite database and create tables"""
        self.conn = sqlite3.connect('student_management.db')
        self.cursor = self.conn.cursor()

        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                enrollment_date DATE DEFAULT CURRENT_DATE,
                address TEXT,
                status TEXT DEFAULT 'Active'
            )
        """)

        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                credits INTEGER DEFAULT 3,
                instructor TEXT,
                description TEXT
            )
        """)

        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                enrollment_date DATE DEFAULT CURRENT_DATE,
                grade TEXT,
                status TEXT DEFAULT 'Enrolled',
                FOREIGN KEY (student_id) REFERENCES students (student_id),
                FOREIGN KEY (course_id) REFERENCES courses (course_id)
            )
        """)

        self.conn.commit()

    def create_widgets(self):
        """Create the main GUI widgets"""
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        
        title_label = ttk.Label(main_frame, text="Student Management System", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        
        self.create_left_panel(main_frame)

        
        self.create_right_panel(main_frame)

        
        self.create_bottom_panel(main_frame)

    def create_left_panel(self, parent):
        """Create left panel with student form"""
        left_frame = ttk.LabelFrame(parent, text="Student Information", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        
        ttk.Label(left_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.first_name_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.first_name_var, width=25).grid(row=0, column=1, pady=5)

        ttk.Label(left_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.last_name_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.last_name_var, width=25).grid(row=1, column=1, pady=5)

        ttk.Label(left_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.email_var, width=25).grid(row=2, column=1, pady=5)

        ttk.Label(left_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.phone_var, width=25).grid(row=3, column=1, pady=5)

        ttk.Label(left_frame, text="Date of Birth:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.dob_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.dob_var, width=25).grid(row=4, column=1, pady=5)
        ttk.Label(left_frame, text="(YYYY-MM-DD)", font=("Arial", 8)).grid(row=4, column=2, sticky=tk.W)

        ttk.Label(left_frame, text="Address:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.address_var = tk.StringVar()
        address_entry = tk.Text(left_frame, width=25, height=3)
        address_entry.grid(row=5, column=1, pady=5)
        self.address_text = address_entry

        ttk.Label(left_frame, text="Status:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="Active")
        status_combo = ttk.Combobox(left_frame, textvariable=self.status_var, 
                                   values=["Active", "Inactive", "Graduated"])
        status_combo.grid(row=6, column=1, pady=5)

    
        search_frame = ttk.LabelFrame(left_frame, text="Search Students", padding="10")
        search_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)

        ttk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=0, column=2)

    def create_right_panel(self, parent):
        """Create right panel with student list"""
        right_frame = ttk.LabelFrame(parent, text="Student List", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        
        columns = ('ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Status')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=20)

        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['First Name', 'Last Name']:
                self.tree.column(col, width=100)
            elif col == 'Email':
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=100)

        
        v_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        
        self.tree.bind('<<TreeviewSelect>>', self.on_student_select)

    def create_bottom_panel(self, parent):
        """Create bottom panel with action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        
        ttk.Button(button_frame, text="Add Student", command=self.add_student, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Student", command=self.update_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Student", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        
        ttk.Button(button_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)

        
        self.selected_student_id = None

    def add_student(self):
        """Add a new student to the database"""
        if not self.validate_form():
            return

        try:
            self.cursor.execute("""
                INSERT INTO students (first_name, last_name, email, phone, date_of_birth, address, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.first_name_var.get().strip(),
                self.last_name_var.get().strip(),
                self.email_var.get().strip(),
                self.phone_var.get().strip(),
                self.dob_var.get().strip() or None,
                self.address_text.get("1.0", tk.END).strip(),
                self.status_var.get()
            ))

            self.conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.clear_form()
            self.refresh_student_list()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {str(e)}")

    def update_student(self):
        """Update selected student"""
        if not self.selected_student_id:
            messagebox.showwarning("Warning", "Please select a student to update")
            return

        if not self.validate_form():
            return

        try:
            self.cursor.execute("""
                UPDATE students 
                SET first_name=?, last_name=?, email=?, phone=?, date_of_birth=?, address=?, status=?
                WHERE student_id=?
            """, (
                self.first_name_var.get().strip(),
                self.last_name_var.get().strip(),
                self.email_var.get().strip(),
                self.phone_var.get().strip(),
                self.dob_var.get().strip() or None,
                self.address_text.get("1.0", tk.END).strip(),
                self.status_var.get(),
                self.selected_student_id
            ))

            self.conn.commit()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.clear_form()
            self.refresh_student_list()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {str(e)}")

    def delete_student(self):
        """Delete selected student"""
        if not self.selected_student_id:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return

        result = messagebox.askyesno("Confirm Delete", 
                                   "Are you sure you want to delete this student? This action cannot be undone.")
        if result:
            try:
                self.cursor.execute("DELETE FROM students WHERE student_id=?", (self.selected_student_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.clear_form()
                self.refresh_student_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {str(e)}")

    def validate_form(self):
        """Validate form inputs"""
        if not self.first_name_var.get().strip():
            messagebox.showerror("Error", "First name is required")
            return False

        if not self.last_name_var.get().strip():
            messagebox.showerror("Error", "Last name is required")
            return False

        if not self.email_var.get().strip():
            messagebox.showerror("Error", "Email is required")
            return False

        
        email = self.email_var.get().strip()
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return False

    
        dob = self.dob_var.get().strip()
        if dob:
            try:
                datetime.strptime(dob, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
                return False

        return True

    def clear_form(self):
        """Clear all form fields"""
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.dob_var.set("")
        self.address_text.delete("1.0", tk.END)
        self.status_var.set("Active")
        self.selected_student_id = None

    def refresh_student_list(self):
        """Refresh the student list in the treeview"""
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        
        self.cursor.execute("""
            SELECT student_id, first_name, last_name, email, phone, status 
            FROM students ORDER BY last_name, first_name
        """)

        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def on_student_select(self, event):
        """Handle student selection in treeview"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']

            
            self.selected_student_id = values[0]

            
            self.cursor.execute("""
                SELECT first_name, last_name, email, phone, date_of_birth, address, status
                FROM students WHERE student_id=?
            """, (self.selected_student_id,))

            student_data = self.cursor.fetchone()
            if student_data:
                self.first_name_var.set(student_data[0])
                self.last_name_var.set(student_data[1])
                self.email_var.set(student_data[2])
                self.phone_var.set(student_data[3] or "")
                self.dob_var.set(student_data[4] or "")

            
                self.address_text.delete("1.0", tk.END)
                if student_data[5]:
                    self.address_text.insert("1.0", student_data[5])

                self.status_var.set(student_data[6])

    def on_search(self, event):
        """Handle search functionality"""
        search_term = self.search_var.get().strip()

        
        for item in self.tree.get_children():
            self.tree.delete(item)

        if search_term:
            
            self.cursor.execute("""
                SELECT student_id, first_name, last_name, email, phone, status 
                FROM students 
                WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY last_name, first_name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            
            self.cursor.execute("""
                SELECT student_id, first_name, last_name, email, phone, status 
                FROM students ORDER BY last_name, first_name
            """)

        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def clear_search(self):
        """Clear search and refresh list"""
        self.search_var.set("")
        self.refresh_student_list()

    def export_csv(self):
        """Export student data to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                self.cursor.execute("""
                    SELECT student_id, first_name, last_name, email, phone, 
                           date_of_birth, enrollment_date, address, status 
                    FROM students ORDER BY last_name, first_name
                """)

                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Phone', 
                                   'Date of Birth', 'Enrollment Date', 'Address', 'Status'])
                    writer.writerows(self.cursor.fetchall())

                messagebox.showinfo("Success", f"Data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def import_csv(self):
        """Import student data from CSV"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    imported_count = 0

                    for row in reader:
                        try:
                            self.cursor.execute("""
                                INSERT INTO students (first_name, last_name, email, phone, 
                                                    date_of_birth, address, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                row.get('First Name', '').strip(),
                                row.get('Last Name', '').strip(),
                                row.get('Email', '').strip(),
                                row.get('Phone', '').strip(),
                                row.get('Date of Birth', '').strip() or None,
                                row.get('Address', '').strip(),
                                row.get('Status', 'Active').strip()
                            ))
                            imported_count += 1
                        except sqlite3.IntegrityError:
                            
                            continue

                    self.conn.commit()
                    self.refresh_student_list()
                    messagebox.showinfo("Success", f"Imported {imported_count} students")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {str(e)}")

    def generate_report(self):
        """Generate a simple text report"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if filename:
                self.cursor.execute("SELECT COUNT(*) FROM students")
                total_students = self.cursor.fetchone()[0]

                self.cursor.execute("SELECT COUNT(*) FROM students WHERE status='Active'")
                active_students = self.cursor.fetchone()[0]

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("STUDENT MANAGEMENT SYSTEM REPORT\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Total Students: {total_students}\n")
                    f.write(f"Active Students: {active_students}\n")
                    f.write(f"Inactive Students: {total_students - active_students}\n\n")

                    
                    f.write("STUDENT LIST:\n")
                    f.write("-" * 20 + "\n")

                    self.cursor.execute("""
                        SELECT first_name, last_name, email, status 
                        FROM students ORDER BY last_name, first_name
                    """)

                    for row in self.cursor.fetchall():
                        f.write(f"{row[1]}, {row[0]} - {row[2]} ({row[3]})\n")

                messagebox.showinfo("Success", f"Report generated: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to run the application"""
    root = tk.Tk()

    
    style = ttk.Style()
    style.theme_use('clam')  

    app = StudentManagementSystem(root)

    
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()

if __name__ == "__main__":
    main()
