     # cursor.execute( f"""
            #                 insert into gardener (first_name, last_name, email, phone_number,address,date_joined, status, username)
            #                 values (NULL,NULL,'{email}',NULL,NULL,CURDATE(),'active','{username}');
            #                 """)
            # connection.commit()

            # Redirect to home page
            # return redirect(url_for('home',username=username))




    # elif request.method == 'POST':
    #     # Form is empty... (no POST data)
    #     msg = 'Please fill out the form!'
    # # Show registration form with message (if any)