from django.shortcuts import render, redirect
from hirenow.db_connection import get_db
from datetime import datetime

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
    all_jobs = list(db.jobs.find())
    
 
    for job in all_jobs:
        job['id_str'] = str(job['_id'])
        
    return render(request, 'jobs/job_list.html', {'jobs': all_jobs})

from bson.objectid import ObjectId
from django.core.files.storage import FileSystemStorage

def apply_job(request, job_id):
    db = get_db()

    job = db.jobs.find_one({"_id": ObjectId(job_id)})

    if request.method == 'POST' and request.FILES.get('resume'):
    
        resume_file = request.FILES['resume']
        fs = FileSystemStorage()
        
        filename = fs.save(resume_file.name, resume_file)
        file_url = fs.url(filename)

        
        application_data = {
            "job_id": job_id,
            "job_title": job['title'],
            "applicant_name": request.POST.get('applicant_name'),
            "resume_url": file_url,
            "applied_at": datetime.now()
        }
        db.applications.insert_one(application_data)
        
        return redirect('job_list') 

    return render(request, 'jobs/apply.html', {'job': job})

def employer_dashboard(request):
    # Security: Kick out anyone who isn't an Admin/Employer
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('job_list')

    db = get_db()
    # Fetch all submitted applications from NoSQL
    all_applications = list(db.applications.find())
    
    return render(request, 'jobs/dashboard.html', {'applications': all_applications})