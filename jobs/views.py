from django.shortcuts import render, redirect
from hirenow.db_connection import get_db
from datetime import datetime
from bson.objectid import ObjectId

def post_job(request):
    if request.method == 'POST':
        
        db = get_db()
        
       
        job_data = {
            "title": request.POST.get('title'),
            "company": request.POST.get('company'),
            "description": request.POST.get('description'),
            "salary": request.POST.get('salary'),
            "posted_at": datetime.now()
        }
        
      
        db.jobs.insert_one(job_data)
        
        return redirect('post_job') 
    return render(request, 'jobs/post_job.html')

def job_list(request):
    db = get_db()
    
    # 1. Look for a search query in the URL (e.g., ?q=developer)
    search_query = request.GET.get('q', '')

    if search_query:
        # 2. Advanced NoSQL Query: Search for matching title OR company (case-insensitive)
        nosql_query = {
            "$or": [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"company": {"$regex": search_query, "$options": "i"}}
            ]
        }
        all_jobs = list(db.jobs.find(nosql_query))
    else:
        # If no search query, just show everything
        all_jobs = list(db.jobs.find())
    
    for job in all_jobs:
        job['id_str'] = str(job['_id'])
        
    return render(request, 'jobs/job_list.html', {
        'jobs': all_jobs, 
        'search_query': search_query # Pass this back to keep the text in the search bar
    })
def apply_job(request, job_id):
    db = get_db()
    job = db.jobs.find_one({'_id': ObjectId(job_id)})

    if request.method == 'POST':
        resume = request.FILES['resume']
        fs = FileSystemStorage()
        filename = fs.save(resume.name, resume)
        
        application = {
            'job_id': job_id,
            'job_title': job['title'],
            'applicant_name': request.POST['applicant_name'],
            'username': request.user.username, # <--- NEW: Links app to the logged-in user
            'status': 'Pending',               # <--- NEW: Default status
            'resume_url': fs.url(filename),
            'applied_at': datetime.datetime.now(datetime.timezone.utc)
        }
        db.applications.insert_one(application)
        # Send seeker to their new dashboard after applying!
        return redirect('seeker_dashboard') 

    return render(request, 'jobs/apply.html', {'job': job})

def employer_dashboard(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('job_list')

    db = get_db()
    all_applications = list(db.applications.find())
    
    # Clean up IDs and statuses for the template
    for app in all_applications:
        app['id_str'] = str(app['_id'])
        if 'status' not in app:
            app['status'] = 'Pending' # Fallback for old test applications
            
    return render(request, 'jobs/dashboard.html', {'applications': all_applications})

def seeker_dashboard(request):
    # Only normal users should see this
    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('employer_dashboard')
        
    db = get_db()
    # NoSQL Query: Find only the applications belonging to this specific user!
    my_applications = list(db.applications.find({'username': request.user.username}))
    
    for app in my_applications:
        if 'status' not in app:
            app['status'] = 'Pending'
            
    return render(request, 'jobs/seeker_dashboard.html', {'applications': my_applications})

def update_status(request, app_id, new_status):
    # Security: Only admins can change status
    if request.user.is_superuser or request.user.role == 'admin':
        db = get_db()
        # NoSQL Update: Find application by ID and change its status
        db.applications.update_one(
            {'_id': ObjectId(app_id)},
            {'$set': {'status': new_status}}
        )
    return redirect('employer_dashboard')