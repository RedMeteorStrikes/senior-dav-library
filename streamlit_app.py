import streamlit as st
import sqlite3
from actions import *

# Connect to SQLite database for books
conn_books = sqlite3.connect('library.db')
cursor_books = conn_books.cursor()

# Create Books table if not exists
cursor_books.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        genre TEXT,
        isbn TEXT,
        publisher TEXT,
        accenture_number TEXT,
        status TEXT DEFAULT 'In-Stock',
        student TEXT,
        date_issued DATE
    )
''')
conn_books.commit()

# Connect to SQLite database for students
conn_students = sqlite3.connect('students.db')
cursor_students = conn_students.cursor()

# Create Students table if not exists with additional fields
cursor_students.execute('''
    CREATE TABLE IF NOT EXISTS students (
        name TEXT,
        grade TEXT,
        section TEXT,
        pl_number TEXT,
        book TEXT
    )
''')
conn_students.commit()

# Streamlit UI
st.title("Library Management System")

# Image on top of everything in the sidebar
image_path = "davLogo.png"
st.sidebar.image(image_path, width=150)

# Sidebar for navigation with dropdown
st.sidebar.subheader("Navigation")

# Dropdown for navigation
navigation_options = ["🏠 Home", "📚 Books", "🧑‍🎓 Students", "📊 Reports", "🔄 Circulation"]
selected_option_index = st.sidebar.selectbox("Select an option", range(len(navigation_options)), format_func=lambda x: navigation_options[x])

# Display selected page
if selected_option_index == 0:
    st.header("🏠 Home")
    st.subheader("Quick Access")

    with st.expander("⬆️ Check-Out"):
        check_out(cursor_books, conn_books, cursor_students, conn_students)

    with st.expander("📃 View Books"):
        view_books(cursor_books)
    
    with st.expander("📃 View Students"):
        view_students(cursor_students)

    with st.expander("⌛Overdue Books"):
        generate_overdue_books_report()

elif selected_option_index == 1:
    st.subheader("📚 Books")

    with st.expander("➕ Add Book"):
        add_book(cursor_books, conn_books)
    
    with st.expander("📃 View Books"):
        view_books(cursor_books)
    
    with st.expander("✏️ Edit Books"):
        edit_books(cursor_books, conn_books)
    
    with st.expander("➖ Remove Books"):
        remove_books(cursor_books, conn_books)

elif selected_option_index == 2:
    st.subheader("🧑‍🎓 Students")

    with st.expander("➕ Add Student"):
        add_student(cursor_students, conn_students)
    
    with st.expander("📃 View Students"):
        view_students(cursor_students)
    
    with st.expander("✏️ Edit Students"):
        edit_students(cursor_students, conn_students)

    with st.expander("➖ Remove Students"):
        remove_students(cursor_students, conn_students)

elif selected_option_index == 3:
    st.subheader("📊 Reports")

    with st.expander("📖 Books Borrowed"):
        generate_books_borrowed_list(cursor_books)

    with st.expander("⌛Overdue Books"):
        generate_overdue_books_report()

    st.subheader("📉Analytics")

    with st.expander("📊 Genre Distribution"):
        display_genre_distribution()

elif selected_option_index == 4:
    st.subheader("🔄 Circulation")

    with st.expander("⬆️ Check-Out"):
        check_out(cursor_books, conn_books, cursor_students, conn_students)

    with st.expander("⬇️ Check-In"):
        check_in(cursor_books, conn_books, cursor_students, conn_students)

    with st.expander("⌚ Extend Due Date"):
            extend_due_date(cursor_books, conn_books)
    
# Close the connections
conn_books.close()
conn_students.close()
