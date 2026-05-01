from django.shortcuts import render, redirect
from hirenow.db_connection import get_db
from datetime import datetime, timezone
from bson.objectid import ObjectId
from django.core.files.storage import FileSystemStorage 

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
    search_query = request.GET.get('q', '')

    if search_query:
        # ==========================================
        # NEW: Full-Text Indexed NoSQL Search
        # ==========================================
        nosql_query = {"$text": {"$search": search_query}}
        
        # We also sort by text "score" so the most relevant results show up first!
        all_jobs = list(db.jobs.find(nosql_query).sort([("score", {"$meta": "textScore"})]))
    else:
        all_jobs = list(db.jobs.find())
    
    for job in all_jobs:
        job['id_str'] = str(job['_id'])
        
    return render(request, 'jobs/job_list.html', {
        'jobs': all_jobs, 
        'search_query': search_query
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
            'username': request.user.username, 
            'status': 'Pending',               
            'resume_url': fs.url(filename),
            'applied_at': datetime.now(timezone.utc)
        }
        db.applications.insert_one(application)
       
        return redirect('seeker_dashboard') 

    return render(request, 'jobs/apply.html', {'job': job})

def employer_dashboard(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('job_list')

    db = get_db()
    
   
    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_counts = list(db.applications.aggregate(status_pipeline))
    
    # Process the pipeline results into a dictionary
    stats = {'Pending': 0, 'Reviewed': 0, 'Accepted': 0, 'Rejected': 0, 'Total': 0}
    for item in status_counts:
        status_key = item['_id'] if item['_id'] else 'Pending'
        stats[status_key] = item['count']
        stats['Total'] += item['count']

    # Pipeline 2: Find the Top 3 most applied-to jobs
    popular_jobs_pipeline = [
        {"$group": {"_id": "$job_title", "total_apps": {"$sum": 1}}},
        {"$sort": {"total_apps": -1}}, # Sort descending
        {"$limit": 3}                  # Only keep top 3
    ]
    popular_jobs = list(db.applications.aggregate(popular_jobs_pipeline))
    
    # FIX: Django templates block keys starting with '_', so we rename '_id' to 'title'
    for job in popular_jobs:
        job['title'] = job['_id']
        
    # ==========================================

    # Get all applications for the table
    all_applications = list(db.applications.find())
    for app in all_applications:
        app['id_str'] = str(app['_id'])
        if 'status' not in app:
            app['status'] = 'Pending'
            
    return render(request, 'jobs/dashboard.html', {
        'applications': all_applications,
        'stats': stats,               
        'popular_jobs': popular_jobs  
    })

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