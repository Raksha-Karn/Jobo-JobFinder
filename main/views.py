from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def home(request):
    try:
        categories = [
            "Python Developer",
            "Data Scientist", 
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "DevOps Engineer",
            "Machine Learning Engineer",
            "Software Engineer",
            "Data Analyst",
            "UI/UX Designer"
        ]
        
        category_data = []
        
        for category in categories:
            response = supabase.table("raw_jobs_data").select("id", count="exact").ilike("title", f"%{category}%").execute()
            count = response.count if hasattr(response, 'count') else 0
            
            category_data.append({
                'name': category,
                'count': count
            })
            
        total_jobs = supabase.table("raw_jobs_data").select("id", count="exact").execute()
        total_jobs_count = total_jobs.count if hasattr(total_jobs, 'count') else 0
        
        companies = supabase.table("raw_jobs_data").select("company_title").execute()
        unique_companies = len(set(job['company_title'] for job in companies.data)) if hasattr(companies, 'data') else 0
        
        stats = {
            'total_jobs': total_jobs_count,
            'companies': unique_companies,
            'job_seekers': '1000+'  
        }
        
        context = {
            'categories': category_data,
            'stats': stats
        }
        
        return render(request, 'home.html', {'categories': category_data, 'stats': stats})
        
    except Exception as e:
        print(f"Error fetching data from Supabase: {str(e)}")
        categories = [
            {'name': 'Python Developer', 'count': 0},
            {'name': 'Data Scientist', 'count': 0},
            {'name': 'Frontend Developer', 'count': 0},
            {'name': 'Backend Developer', 'count': 0},
            {'name': 'Full Stack Developer', 'count': 0},
            {'name': 'DevOps Engineer', 'count': 0},
            {'name': 'Machine Learning Engineer', 'count': 0},
            {'name': 'Software Engineer', 'count': 0},
            {'name': 'Data Analyst', 'count': 0},
            {'name': 'UI/UX Designer', 'count': 0}
        ]
        stats = {
            'total_jobs': 0,
            'companies': 0,
            'job_seekers': '1M+'
        }
        return render(request, 'home.html', {'categories': categories, 'stats': stats})

def jobs_view(request):
    try:
        query = supabase.table("raw_jobs_data").select("*")
        
        search_term = request.GET.get('search', '').strip()
        job_type_filter = request.GET.get('job_type', '').strip()
        location_filter = request.GET.get('location', '').strip()
        view_mode = request.GET.get('view', 'grid')  
        
        if search_term:
            query = query.ilike("title", f"%{search_term}%")
        
        if job_type_filter:
            query = query.eq("job_type", job_type_filter)
            
        if location_filter:
            query = query.ilike("location", f"%{location_filter}%")
        
        response = query.order("created_at", desc=True).execute()
        all_jobs = response.data if hasattr(response, 'data') else []
        
        all_jobs_response = supabase.table("raw_jobs_data").select("job_type").execute()
        job_data = all_jobs_response.data if hasattr(all_jobs_response, 'data') else []
        
        job_types = sorted(list(set(job['job_type'] for job in job_data if job.get('job_type'))))
        
        page = request.GET.get('page', 1)
        paginator = Paginator(all_jobs, 15)  
        
        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)
        
    except Exception as e:
        print(f"Error fetching jobs from Supabase: {str(e)}")
        jobs = []
        job_types = []
        paginator = None
        view_mode = 'grid'
    
    context = {
        'jobs': jobs,
        'job_count': len(all_jobs),
        'job_types': job_types,
        'search_term': search_term,
        'job_type_filter': job_type_filter,
        'location_filter': location_filter,
        'is_paginated': True if paginator and paginator.num_pages > 1 else False,
        'view_mode': view_mode
    }
    return render(request, 'jobs.html', context)
