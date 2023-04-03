from django.core.mail import EmailMessage
import io
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.core.mail import send_mail
from myproject import settings
from django.contrib.auth.decorators import login_required
import base64
import qrcode 
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

class MyPasswordResetView(PasswordResetView):
    email_template_name = 'authsystem/password_reset_email.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'authsystem/password_reset.html'




#home view 
def home(request):
    return render(request, 'authsystem/home.html')





#Register view 

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2'] 


        
        if User.objects.filter(email = email):
            messages.error(request, f"The email:{email} already exists")
            return redirect('register')
        if User.objects.filter(username = username):
            messages.error(request, f'The  username:{username} has an account already')
            return redirect('register')
        if pass1 != pass2:
            messages.error(request, 'passwords do not match')
            return redirect('register')
        
        user = User.objects.create_user(username, email,pass1)
        user.save()
        messages.success(request, f'{username} you account has been created successfully')
        subject = 'Welcome to QR code authentication system project'
        message = " hello \n Welcome to QR code authentication system project  \n Thank you for registering at our website"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject,message,from_email, to_list,fail_silently = True)
        

        return redirect('signin')

    return render(request, 'authsystem/register1.html')


#login view 

def LoginUser(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1, email=email)
            
        if user is not None:
            login(request, user)
           
            token = request.session.session_key
            # Generate a QR code for the token
            qr = qrcode.make(token)
            # Create an in-memory stream for the QR code image
            qr_stream = io.BytesIO()
            qr.save(qr_stream, "PNG")

            token_b64 = base64.b64encode(token.encode("utf-8")).decode("utf-8")
            # Attach the QR code image to an email and send it to the user's email address
            email = EmailMessage(
                subject="QR Code Authentication",
                body="To login in to our website with qr code you can simply follow this link to view the qrcode http://localhost:8000/sendqrcode/ and Scan to get authenticated",
                to=[user.email],
                headers={"X-QR-Token": token_b64},
            )
            #email.attach("qr_code.png", qr_stream.getvalue(), "image/png")
            email.send(fail_silently=True)
            messages.success(request, f' {username} you have logged in successfully')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('signin')
    
    return render(request, 'authsystem/login1.html')


#display qrcode view 

def QRCodeView(request):
    # Render the QR code scanning page
    # Generate a new session key for the user
    request.session.cycle_key()
    token = request.session.session_key

    # Save the session key in the user's session
    request.session['qr_token'] = token

    # Generate a QR code for the token
    qr = qrcode.make(token)

    # Create an in-memory stream for the QR code image
    qr_stream = io.BytesIO()
    qr.save(qr_stream, "PNG")

   

    # Encode the session key as base64 for use in the X-QR-Token header
    token_b64 = base64.b64encode(token.encode("utf-8")).decode("utf-8")

    context = {
        'qr_token': token
    }

    return render(request, 'authsystem/qrcode.html', context)




#Authenticate qrcode view 

def AuthenticateUser(request):
    if request.method == 'POST':
        # Decode the token from the X-QR-Token header
        token_b64 = request.META.get('HTTP_X_QR_TOKEN')
        token = base64.b64decode(token_b64.encode("utf-8")).decode("utf-8")

        # Check if the token matches the one stored in the user's session
        if token == request.session.get('qr_token'):
            # If the token matches, log the user in and redirect to the home page
            user = request.user
            login(request, user)
            messages.success(request, f'{user.username}, you have logged in successfully')
            return redirect('home')
        else:
            # If the token does not match, show an error message
            messages.error(request, 'Authentication failed. Please try again.')
            return redirect('signin')
    return render(request, 'authsystem/authenticate.html') 


def forgotpassword(request):
    return render(request, 'authsystem/resetpassword.html')