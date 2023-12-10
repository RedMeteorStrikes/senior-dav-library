#Imports

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import Workbook
import base64
import io

#Books

def add_book(cursor, conn):
    st.subheader("Add a Book")

    form = st.form(key="add_book_form")

    title = form.text_input("Title")
    author = form.text_input("Author")
    genre = form.text_input("Genre")
    isbn = form.text_input("ISBN")
    publisher = form.text_input("Publisher")
    accenture_number = form.text_input("Accenture Number")

    submit_button = form.form_submit_button("Add Book")

    if submit_button:
        cursor.execute('''
            INSERT INTO books (title, author, genre, isbn, publisher, accenture_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, genre, isbn, publisher, accenture_number, 'In-Stock'))
        conn.commit()
        st.success("Book added successfully!")
def view_books(cursor):
    st.subheader("View Books")

    search_term = st.text_input("Search for books:")

    if search_term:
        query = f"SELECT * FROM books WHERE title LIKE '%{search_term}%' OR author LIKE '%{search_term}%' OR genre LIKE '%{search_term}%' OR isbn LIKE '%{search_term}%' OR publisher LIKE '%{search_term}%' OR accenture_number LIKE '%{search_term}%'"
        cursor.execute(query)
        books = cursor.fetchall()
    else:
        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()

    # Update columns list based on your actual column names
    columns = ["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]  # Update columns list

    # Create DataFrame using fetched data and specified columns
    df_books = pd.DataFrame(books, columns=columns)

    st.table(df_books.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))
def remove_books(cursor, conn):
    st.subheader("Remove Books")

    remove_search_term = st.text_input("Search for books to remove:")

    remove_query = f"SELECT * FROM books WHERE (title LIKE '%{remove_search_term}%' OR author LIKE '%{remove_search_term}%' OR genre LIKE '%{remove_search_term}%' OR isbn LIKE '%{remove_search_term}%' OR publisher LIKE '%{remove_search_term}%' OR accenture_number LIKE '%{remove_search_term}%')"
    cursor.execute(remove_query)
    remove_books_data = cursor.fetchall()

    remove_columns = ["Serial Number", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]
    df_remove_books = pd.DataFrame(remove_books_data, columns=remove_columns)

    st.table(df_remove_books.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))

    selected_books_remove = st.checkbox("Select All (Remove)")
    books_to_remove = []
    for book_remove in remove_books_data:
        checkbox_key_remove = f"remove_{book_remove[0]}"
        selected_remove = st.checkbox(book_remove[1], key=checkbox_key_remove)

        if selected_books_remove:
            books_to_remove.append(book_remove[0])
        elif selected_remove:
            books_to_remove.append(book_remove[0])

    if st.button("Remove Books"):
        for book_id_remove in books_to_remove:
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id_remove,))
        conn.commit()
        st.success("Books removed successfully!")
def edit_books(cursor, conn):
    st.subheader("Edit Books")

    # Fetch the list of books for selection
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()

    # Convert the book data to a Pandas DataFrame
    df_books = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Dat Issued"])

    # Search bar for filtering books
    search_term = st.text_input("Books Search", key="books_search")  # Unique key for the search input

    # Filter books based on the search term
    if search_term:
        filtered_books = df_books[df_books.apply(lambda row: any(search_term.lower() in str(value).lower() for value in row), axis=1)]
    else:
        filtered_books = df_books.copy()

    # Display the table of books
    st.write("Books Table:")
    st.table(filtered_books[["Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student"]])

    # Checkboxes for book selection
    selected_books = []
    for index, book in filtered_books.iterrows():
        checkbox = st.checkbox(f"{book['Title']}")
        if checkbox:
            selected_books.append(book)

    # Input fields for selected book attributes
    for book in selected_books:
        st.write(f"Editing Details for Book: {book['Title']}")
        new_title = st.text_input("New Title", value=book['Title'])
        new_author = st.text_input("New Author", value=book['Author'])
        new_genre = st.text_input("New Genre", value=book['Genre'])
        new_isbn = st.text_input("New ISBN", value=book['ISBN'])
        new_publisher = st.text_input("New Publisher", value=book['Publisher'])
        new_accenture_number = st.text_input("New Accenture Number", value=book['Accenture Number'])

    # Confirm button to update book details
    if st.button("Confirm"):
        for book in selected_books:
            cursor.execute('''
                UPDATE books 
                SET title = ?, author = ?, genre = ?, isbn = ?, publisher = ?, accenture_number = ?
                WHERE id = ?
            ''', (new_title, new_author, new_genre, new_isbn, new_publisher, new_accenture_number, book['ID']))
            conn.commit()
            st.success(f"{book['Title']} details updated successfully!")

#Circulation

def check_in(cursor_books, conn_books, cursor_students, conn_students):
    st.subheader("Check-In")
    student_info_requested = True

    # Fetch issued books
    cursor_books.execute('SELECT * FROM books WHERE status = "Issued"')
    issued_books = cursor_books.fetchall()

    columns_check_in = ["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]
    df_check_in = pd.DataFrame(issued_books, columns=columns_check_in)

    search_check_in = st.text_input("Search for books to check-in:")
    if search_check_in:
        df_check_in = df_check_in[df_check_in.apply(lambda row: any(search_check_in.lower() in str(value).lower() for value in row), axis=1)]

    st.table(df_check_in.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))

    selected_books_check_in = st.checkbox("Select All (Check-In)")
    books_to_check_in = []
    for index, issued_book in df_check_in.iterrows():
        checkbox_key = f"check_in_{issued_book['ID']}"
        selected_check_in = st.checkbox(issued_book['Title'], key=checkbox_key)

        if selected_books_check_in:
            books_to_check_in.append(issued_book['ID'])
        elif selected_check_in:
            books_to_check_in.append(issued_book['ID'])

    if st.button("Get Student"):
        student_info_requested = True
        for book_id_check_in in books_to_check_in:
            cursor_books.execute('SELECT * FROM books WHERE ID = ?', (book_id_check_in,))
            selected_issued_book = cursor_books.fetchone()

            cursor_students.execute('SELECT * FROM students WHERE pl_number = ?', (selected_issued_book[8],))
            selected_student = cursor_students.fetchone()

            st.table(pd.DataFrame([selected_student], columns=["Name", "Grade", "Section", "PL Number", "Book"]).style.set_table_styles([{'selector': 'table', 'props': [('height', '100px')]}]))

    if student_info_requested and st.button("Check-In"):
        for book_id_check_in in books_to_check_in:
            cursor_books.execute('SELECT * FROM books WHERE ID = ?', (book_id_check_in,))
            selected_issued_book = cursor_books.fetchone()

            cursor_students.execute('SELECT * FROM students WHERE pl_number = ?', (selected_issued_book[8],))
            selected_student = cursor_students.fetchone()

            # Update book status and date_issued column
            cursor_books.execute('UPDATE books SET status = "In-Stock", date_issued = "Not Available", student = "Not Available" WHERE ID = ?', (book_id_check_in,))

            #Update the student's book to "Not Available"
            cursor_students.execute('UPDATE students SET book = "Not Available" WHERE pl_number = ?', (selected_issued_book[8],))

        conn_books.commit()
        conn_students.commit()
        st.rerun()
        st.success("Books checked in successfully!")
def check_out(cursor, conn, cursor_students, conn_students):
    st.subheader("Check-Out")

    books_to_check_out = []
    students_to_check_out = []

    # Initialize selected student variable
    selected_student = None

    # Display form for selecting books and entering student information
    with st.form(key="form_check_out"):
        # Search box for check-out books
        search_check_out_books = st.text_input("Search for books to check-out:")

        # Get the list of in-stock books
        cursor.execute('SELECT * FROM books WHERE status = "In-Stock"')

        # Apply search filter
        if search_check_out_books:
            books_out = [book for book in cursor.fetchall() if any(search_check_out_books.lower() in str(value).lower() for value in book)]
        else:
            books_out = cursor.fetchall()

        # Display checkboxes for each book
        for index, book_out in enumerate(books_out):
            checkbox_key_out = f"check_out_book_{book_out[0]}"
            selected_check_out = st.checkbox(book_out[1], key=checkbox_key_out)
            if selected_check_out:
                books_to_check_out.append(book_out[0])

        # Display filtered books in tabular format
        table_data_books = pd.DataFrame(books_out, columns=["Serial Number", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"])
        st.table(table_data_books.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))

        # Form input for student search
        student_search = st.text_input("Search for Student")

        # Search button for the form
        if student_search:
            # Search for the student in the database
            cursor_students.execute('SELECT * FROM students WHERE name LIKE ? OR pl_number LIKE ? OR grade || section LIKE ?',
                                    (f'%{student_search}%', f'%{student_search}%', f'%{student_search}%'))
            existing_students = cursor_students.fetchall()

            if existing_students:
                # Display student details in a table inside the form
                columns_student = ["Name", "Grade", "Section", "PL Number", "Book"]
                df_existing_students = pd.DataFrame(existing_students, columns=columns_student)
                st.table(df_existing_students.style.set_table_styles([{'selector': 'table', 'props': [('height', '100px')]}]))

                # Checkbox for selecting the student
                for existing_student in existing_students:
                    selected_student = st.checkbox(existing_student[0], key=f"select_student_{existing_student[3]}")
                    if selected_student:
                        students_to_check_out.append(existing_student[3])

        if st.form_submit_button("Check-Out"):
        # Perform the check-out logic
            if selected_student and books_to_check_out:
                for book_id_check_out in books_to_check_out:
                    # Update the book status to "Issued" and set the date_issued to the current date
                    cursor.execute('UPDATE books SET status = "Issued", student = ?, date_issued = ? WHERE id = ?',
                                (existing_student[3], datetime.today().strftime('%Y-%m-%d'), book_id_check_out))

                    # Get the Accenture Number of the selected book
                    selected_book_accenture_number = [book_out[6] for book_out in books_out if book_out[0] == book_id_check_out][0]

                    # Update the student's book to the Accenture Number of the selected book
                    cursor_students.execute('UPDATE students SET book = ? WHERE pl_number = ?',(selected_book_accenture_number, existing_student[3]))

                conn.commit()
                conn_students.commit()
                st.rerun()
                st.success("Books checked out successfully!")
                
#Students

def add_student(cursor_students, conn_students):
    st.subheader("Add a Student")

    form = st.form(key="add_student_form")

    name = form.text_input("Name")
    grade = form.text_input("Grade")
    section = form.text_input("Sub-division")
    pl_number = form.text_input("PL Number")

    submit_button = form.form_submit_button("Add Student")

    if submit_button:
        cursor_students.execute('''
            INSERT INTO students (name, grade, section, pl_number, book)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, grade, section, pl_number, 'Not Available'))
        conn_students.commit()
        st.success("Student added successfully!")
def view_students(cursor_students):
    st.subheader("View Students")

    # Search box for students
    search_term_students = st.text_input("Search for students:")

    if search_term_students:
        query_students = f"SELECT * FROM students WHERE name LIKE '%{search_term_students}%' OR pl_number LIKE '%{search_term_students}%' OR grade || section LIKE '%{search_term_students}%'"
        cursor_students.execute(query_students)
        students_data = cursor_students.fetchall()
    else:
        cursor_students.execute('SELECT * FROM students')
        students_data = cursor_students.fetchall()

    # Display students in tabular format
    columns_students = ["Name", "Grade", "Section", "PL Number", "Book"]
    df_students = pd.DataFrame(students_data, columns=columns_students)

    st.table(df_students.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))
def remove_students(cursor_students, conn_students):
    st.subheader("Remove Students")

    remove_search_term_students = st.text_input("Search for students to remove:")

    remove_query_students = f"SELECT * FROM students WHERE name LIKE '%{remove_search_term_students}%' OR pl_number LIKE '%{remove_search_term_students}%' OR grade || section LIKE '%{remove_search_term_students}%'"
    cursor_students.execute(remove_query_students)
    remove_students_data = cursor_students.fetchall()

    remove_columns_students = ["Name", "Grade", "Section", "PL Number", "Book"]
    df_remove_students = pd.DataFrame(remove_students_data, columns=remove_columns_students)

    st.table(df_remove_students.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))

    selected_students_remove = st.checkbox("Select All (Remove)")
    students_to_remove = []
    for student_remove in remove_students_data:
        checkbox_key_remove_students = f"remove_student_{student_remove[3]}"
        selected_remove_students = st.checkbox(student_remove[0], key=checkbox_key_remove_students)

        if selected_students_remove:
            students_to_remove.append(student_remove[3])
        elif selected_remove_students:
            students_to_remove.append(student_remove[3])

    if st.button("Remove Students"):
        for student_id_remove in students_to_remove:
            cursor_students.execute('DELETE FROM students WHERE pl_number = ?', (student_id_remove,))
        conn_students.commit()
        st.success("Students removed successfully!")
def edit_students(cursor_students, conn_students):
    st.subheader("Edit Students")

    # Fetch the list of students for selection
    cursor_students.execute('SELECT * FROM students')
    students = cursor_students.fetchall()

    # Convert student data to a Pandas DataFrame
    df_students = pd.DataFrame(students, columns=["Name", "Grade", "Section", "PL Number", "Book"])

    # Search bar for filtering students
    search_term_students = st.text_input("Search Students", key="students_search")  # Unique key for the search input

    # Filter students based on the search term
    if search_term_students:
        filtered_students = df_students[df_students.apply(lambda row: any(search_term_students.lower() in str(value).lower() for value in row), axis=1)]
    else:
        filtered_students = df_students.copy()

    # Display the table of students
    st.write("Students Table:")
    st.table(filtered_students[["Name", "Grade", "Section", "PL Number", "Book"]])

    # Checkboxes for student selection
    selected_students = []
    for index, student in filtered_students.iterrows():
        checkbox = st.checkbox(f"{student['Name']}")
        if checkbox:
            selected_students.append(student)

    # Input fields for selected student attributes
    for student in selected_students:
        st.write(f"Editing Details for Student: {student['Name']}")
        new_name = st.text_input("New Name", value=student['Name'])
        new_grade = st.text_input("New Grade", value=student['Grade'])
        new_section = st.text_input("New Section", value=student['Section'])
        new_pl_number = st.text_input("New PL Number", value=student['PL Number'])
        new_book = st.text_input("New Book", value=student['Book'])

    # Confirm button to update student details
    if st.button("Confirm"):
        for student in selected_students:
            cursor_students.execute('''
                UPDATE students 
                SET name = ?, grade = ?, section = ?, pl_number = ?, book = ?
                WHERE pl_number = ?
            ''', (new_name, new_grade, new_section, new_pl_number, new_book, student['PL Number']))
            conn_students.commit()
            st.success(f"{student['Name']} details updated successfully!")

#Reports

def generate_books_borrowed_excel(borrowed_books):
    wb = Workbook()
    ws = wb.active

    columns = ["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]
    ws.append(columns)

    for book in borrowed_books:
        ws.append(book)

    ws.column_dimensions['J'].width = 15

    # Save the workbook to a BytesIO object
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    # Prepare Excel file for download
    b64 = base64.b64encode(excel_file.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="borrowed_books_list.xlsx">Download Excel File</a>'
    st.markdown(href, unsafe_allow_html=True)
def generate_books_borrowed_list(cursor):
    st.subheader("Books Borrowed")

    # Search bar for filtering borrowed books
    search_borrowed_books = st.text_input("Search for borrowed books:")

    cursor.execute('SELECT * FROM books WHERE Student IS NOT NULL AND Student != "Not Available"')
    borrowed_books = cursor.fetchall()

    if search_borrowed_books:
        borrowed_books = [book for book in borrowed_books if any(search_borrowed_books.lower() in str(value).lower() for value in book)]

    if borrowed_books:
        columns = ["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]
        df_borrowed_books = pd.DataFrame(borrowed_books, columns=columns)
        
        generate_books_borrowed_excel(borrowed_books)

        st.table(df_borrowed_books)

    else:
        st.warning("No books are currently borrowed.")

def generate_overdue_books_excel(overdue_books):
    wb = Workbook()
    ws = wb.active

    columns = ["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]
    ws.append(columns)

    for book in overdue_books:
        ws.append(book)

    # Set column width for the "Date Issued" column (assuming it's the 10th column)
    ws.column_dimensions['J'].width = 15  # Adjust the width as needed

    # Save the workbook to a BytesIO object
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    # Prepare Excel file for download
    b64 = base64.b64encode(excel_file.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="overdue_books_list.xlsx">Download Excel File</a>'
    st.markdown(href, unsafe_allow_html=True)
def generate_overdue_books_report():
    conn = sqlite3.connect('library.db')  # Connect to your SQLite database
    cursor = conn.cursor()

    st.subheader("Overdue Books")

    # Search bar for filtering overdue books
    search_overdue_books = st.text_input("Search for overdue books:")

    # Calculate the date 7 days ago from the current date
    seven_days_ago = datetime.now() - timedelta(days=7)

    # Fetch overdue books
    if search_overdue_books:
        cursor.execute('SELECT * FROM books WHERE status = "Issued" AND date_issued < ? AND (title LIKE ? OR author LIKE ? OR genre LIKE ? OR isbn LIKE ? OR publisher LIKE ? OR accenture_number LIKE ?)',
                       (seven_days_ago.date(), f'%{search_overdue_books}%', f'%{search_overdue_books}%', f'%{search_overdue_books}%', f'%{search_overdue_books}%', f'%{search_overdue_books}%', f'%{search_overdue_books}%'))
    else:
        cursor.execute('SELECT * FROM books WHERE status = "Issued" AND date_issued < ?', (seven_days_ago.date(),))

    overdue_books = cursor.fetchall()
    conn.close()

    if overdue_books:
        columns = ["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]
        df_overdue_books = pd.DataFrame(overdue_books, columns=columns)

        generate_overdue_books_excel(overdue_books)

        st.table(df_overdue_books.style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))

    else:
        st.info("No overdue books found.")

def fetch_genre_data():
    # Connect to the database
    conn_books = sqlite3.connect('library.db')
    cursor_books = conn_books.cursor()

    # Fetch genre data
    cursor_books.execute('SELECT genre, COUNT(*) as count FROM books GROUP BY genre')
    genre_data = cursor_books.fetchall()

    # Close the connection
    conn_books.close()
    
    return genre_data
def display_genre_distribution():
    st.title('Library Analytics')

    # Fetch genre data
    genre_data = fetch_genre_data()

    # Display a bar chart
    if genre_data:
        df_genre = pd.DataFrame(genre_data, columns=['Genre', 'Count'])
        st.subheader('Genre Distribution')
        st.bar_chart(df_genre.set_index('Genre'))
    else:
        st.info("No genre data available.")

def extend_due_date(cursor_books, conn_books):
    st.subheader("Extend Due Date")

    # Fetch issued books
    cursor_books.execute('SELECT * FROM books WHERE status = "Issued"')
    issued_books = cursor_books.fetchall()

    search_term_extend = st.text_input("Search for books to extend:")

    if search_term_extend:
        issued_books = [book for book in issued_books if any(search_term_extend.lower() in str(value).lower() for value in book)]

    st.table(pd.DataFrame(issued_books, columns=["ID", "Title", "Author", "Genre", "ISBN", "Publisher", "Accenture Number", "Status", "Student", "Date Issued"]).style.set_table_styles([{'selector': 'table', 'props': [('height', '500px')]}]))

    selected_books_extend = st.checkbox("Select All (Extend)")
    books_to_extend = []
    for issued_book in issued_books:
        checkbox_key_extend = f"extend_{issued_book[0]}"
        selected_extend = st.checkbox(issued_book[1], key=checkbox_key_extend)

        if selected_books_extend:
            books_to_extend.append(issued_book[0])
        elif selected_extend:
            books_to_extend.append(issued_book[0])

    if st.button("Extend Due Date"):
        for book_id_extend in books_to_extend:
            cursor_books.execute('UPDATE books SET date_issued = ?, status = "Issued" WHERE ID = ?', (datetime.today().strftime('%Y-%m-%d'), book_id_extend))
            conn_books.commit()

            st.rerun()
            st.success("The book's validity has been extended by another week.")