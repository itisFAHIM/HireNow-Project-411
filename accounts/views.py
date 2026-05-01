from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user)
            return redirect('job_list') 
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        # Check if they actually uploaded a file
        if 'profile_pic' in request.FILES:
            request.user.profile_pic = request.FILES['profile_pic']
            request.user.save()
            return redirect('profile') # Refresh the page to show new image
            
    return render(request, 'accounts/profile.html')