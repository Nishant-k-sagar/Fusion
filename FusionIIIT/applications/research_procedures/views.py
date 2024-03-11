from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from applications.research_procedures.models import *
from applications.globals.models import ExtraInfo, HoldsDesignation, Designation
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from notification.views import research_procedures_notif
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
from .models import *
from collections import defaultdict

# Faculty can file patent and view status of it.

@login_required
def patent_registration(request):

   
    return render(request ,"rs/research.html")

@login_required
#dean_rspc can update status of patent.   
def patent_status_update(request):
    
    user = request.user
    user_extra_info = ExtraInfo.objects.get(user=user)
    user_designations = HoldsDesignation.objects.filter(user=user)
    if request.method=='POST':
        if(user_designations.exists()):
            if(user_designations.first().designation.name == "dean_rspc" and user_extra_info.user_type == "faculty"):
                patent_application_id = request.POST.get('id')
                patent = Patent.objects.get(application_id=patent_application_id)
                patent.status = request.POST.get('status')
                patent.save()
                messages.success(request, 'Patent status updated successfully')
                # Create a notification for the user about the patent status update
                dean_rspc_user = HoldsDesignation.objects.get(designation=Designation.objects.filter(name='dean_rspc').first()).working
                research_procedures_notif(dean_rspc_user,patent.faculty_id.user,request.POST.get('status'))
            else:
                messages.error(request, 'Only Dean RSPC can update status of patent')
    return redirect(reverse("research_procedures:patent_registration"))

@login_required
def research_group_create(request):
    
    user = request.user
    user_extra_info = ExtraInfo.objects.get(user=user)
    if request.method=='POST':
        if user_extra_info.user_type == "faculty":
            form = ResearchGroupForm(request.POST)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Research group created successfully')
        else:
            messages.error(request, 'Only Faculty can create research group')
    return redirect(reverse("research_procedures:patent_registration"))

@login_required
def project_insert(request):
    user = get_object_or_404(ExtraInfo, user=request.user)
    pf = user.id

    research_project = ResearchProject()
    research_project.user = request.user
    research_project.pf_no = pf
    research_project.pi = request.POST.get('pi')
    research_project.co_pi = request.POST.get('co_pi')
    research_project.title = request.POST.get('title')
    research_project.financial_outlay = request.POST.get('financial_outlay')
    research_project.funding_agency = request.POST.get('funding_agency')
    research_project.status = request.POST.get('status')
    x = request.POST.get('start')
    if x[:5] == "Sept." :
        x = "Sep." + x[5:]
    if (request.POST.get('start') != None and request.POST.get('start') != '' and request.POST.get('start') != 'None'):
        try:
            research_project.start_date = datetime.datetime.strptime(x, "%B %d, %Y")
        except:
            research_project.start_date = datetime.datetime.strptime(x, "%b. %d, %Y")
    x = request.POST.get('end')
    if x[:5] == "Sept." :
        x = "Sep." + x[5:]
    if (request.POST.get('end') != None and request.POST.get('end') != '' and request.POST.get('end') != 'None'):
        try:
            research_project.finish_date = datetime.datetime.strptime(x, "%B %d, %Y")
        except:
            research_project.finish_date = datetime.datetime.strptime(x, "%b. %d, %Y")
    x = request.POST.get('sub')
    if x[:5] == "Sept." :
        x = "Sep." + x[5:]
    if (request.POST.get('sub') != None and request.POST.get('sub') != '' and request.POST.get('sub') != 'None'):
        try:
            research_project.date_submission = datetime.datetime.strptime(x, "%B %d, %Y")
        except:
            research_project.date_submission = datetime.datetime.strptime(x, "%b. %d, %Y")
    research_project.save()
    messages.success(request, 'Successfully created research project')
    return redirect(reverse("research_procedures:patent_registration"))

@login_required
def consult_insert(request):
    user = get_object_or_404(ExtraInfo, user=request.user)
    pf = user.id
    consultancy_project = ConsultancyProject()
    consultancy_project.user = request.user
    consultancy_project.pf_no = pf
    consultancy_project.consultants = request.POST.get('consultants')
    consultancy_project.client = request.POST.get('client')
    consultancy_project.title = request.POST.get('title')
    consultancy_project.financial_outlay = request.POST.get('financial_outlay')
    x = request.POST.get('start')
    if x[:5] == "Sept." :
        x = "Sep." + x[5:]
    if (request.POST.get('start') != None and request.POST.get('start') != '' and request.POST.get('start') != 'None'):
        try:
            consultancy_project.start_date = datetime.datetime.strptime(x, "%B %d, %Y")
        except:
            consultancy_project.start_date = datetime.datetime.strptime(x, "%b. %d, %Y")
    x = request.POST.get('end')
    if x[:5] == "Sept." :
        x = "Sep." + x[5:]
    if (request.POST.get('end') != None and request.POST.get('end') != '' and request.POST.get('end') != 'None'):
        try:
            consultancy_project.end_date = datetime.datetime.strptime(x, "%B %d, %Y")
        except:
            consultancy_project.end_date = datetime.datetime.strptime(x, "%b. %d, %Y")
    consultancy_project.save()
    messages.success(request,"Successfully created consultancy project")
    return redirect(reverse("research_procedures:patent_registration"))

def add_projects(request):
    if request.method== "POST":
        obj= request.POST
        projectname= obj.get('project_name')
        projecttype= obj.get('project_type')
        fo= obj.get('financial_outlay')
        pid= obj.get('project_investigator_id')
        copid=obj.get('co_project_investigator_id')
        sa= obj.get('sponsored_agency')
        startd= obj.get('start_date')
        subd= obj.get('finish_date')
        finishd= obj.get('finish_date')
        years= obj.get('number_of_years')
        project_description= obj.get('description')

        check = User.objects.filter(username=pid) 
        print(check[0].username)
       
        
        check= HoldsDesignation.objects.filter(user__username=pid , designation__name= "Professor")
        if not check.exists():
                check= HoldsDesignation.objects.filter(user__username=pid , designation__name= "Assistant Professor")

                if not check.exists():
                    messages.error(request,"Request not added, no such project investigator exists 2")
                    return render(request,"rs/projects.html")  

        
        check= HoldsDesignation.objects.filter(user__username=copid , designation__name= "Professor")
        if not check.exists():
                check= HoldsDesignation.objects.filter(user__username=copid , designation__name= "Assistant Professor")

                if not check.exists():
                    messages.error(request,"Request not added, no such project investigator exists 2")
                    return render(request,"rs/projects.html")  

        
        obj= projects.objects.all()
        if len(obj)==0 :
            projectid=1
        
        else :
            projectid= obj[0].project_id+1

        userpi_instance = User.objects.get(username=pid)
        usercpi_instance = User.objects.get(username=copid)

        projects.objects.create(
            project_id=projectid,
            project_name=projectname,
            project_type=projecttype, 
            status=0,
            project_investigator_id=userpi_instance,
            co_project_investigator_id=usercpi_instance,
            sponsored_agency=sa,
            start_date=startd,
            submission_date=finishd,
            finish_date=finishd,
            years=years,
            project_description=project_description
        )

        messages.success(request,"Project added successfully")
        categories = category.objects.all()

        data = {
            "pid": pid,
            "years": list(range(1, int(years) + 1)),    
            "categories": categories,
        }
       
        # return render(request,'rs/add_financial_outlay.html', context=data)
    return render(request,"rs/projects.html")

def add_fund_requests(request,pj_id):
    data= {
        "pj_id": pj_id
    }
    return render(request,"rs/add_fund_requests.html",context=data)

def add_staff_requests(request,pj_id):
    data= {
        "pj_id": pj_id  
    }
    return render(request,"rs/add_staff_requests.html",context=data)

def add_requests(request,id,pj_id):
    if request.method == 'POST':
        obj=request.POST


        if(id=='0') :  
            projectid = pj_id
            reqtype = obj.get('request_type')
            stats =0
            desc= obj.get('description')    
            amt= obj.get('amount')

            check= projects.objects.filter(project_id=projectid)
            if not check.exists():
                messages.error(request,"Request not added, no such project exists")
                return render(request,"rs/add_fund_requests.html")

            check= projects.objects.filter(project_id= projectid, project_investigator_id__username=pi_id)
            if not check.exists():
                messages.error(request,"Request not added, no such project investigator exists")
                return render(request,"rs/add_fund_requests.html")


            pi_id_instance=User.objects.get(username= request.user.username )
            project_instance=projects.objects.get(project_id=projectid)

            obj= requests.objects.all()
            if len(obj)==0 :
                requestid=1
            
            else :
                requestid= obj[0].request_id+1

            requests.objects.create(
                request_id=requestid,
                project_id=project_instance,
                request_type="funds",
                project_investigator_id=pi_id_instance,
                status=stats, description=desc, amount= amt
            )
            rspc_inventory.objects.create(
                inventory_id=requestid,
                project_id=project_instance,
                project_investigator_id=pi_id_instance,
                status=stats,
                description=desc, amount= amt
            )
            messages.success(request,"Request added successfully")
            return render(request,"rs/add_fund_requests.html")

        if(id=='1'):
            projectid = obj.get('project_id')
            pi_id = obj.get('project_investigator_id')
            stats = obj.get('status')
            desc= obj.get('description')

            obj= requests.objects.all()
            if len(obj)==0 :
                requestid=1
            
            else :
                requestid= obj[0].request_id+1


            check= projects.objects.filter(project_id=projectid)
            if not check.exists():
                messages.error(request,"Request not added, no such project exists")
                return render(request,"rs/add_fund_requests.html")

            check= projects.objects.filter(project_id= projectid, project_investigator_id__username=pi_id)
            if not check.exists():
                messages.error(request,"Request not added, no such project investigator exists")
                return render(request,"rs/add_fund_requests.html")

            pi_id_instance=User.objects.get(username=pi_id)
            project_instance=projects.objects.get(project_id=projectid)

            requests.objects.create(
                    request_id=requestid,
                    project_id=project_instance,
                    request_type="staff",
                    project_investigator_id=pi_id_instance,
                    description=desc
                )
        messages.success(request,"Request added successfully")
        return redirect("/research_procedures")
    return render(request, "rs/add_requests.html")    


def view_projects(request):
    queryset= projects.objects.all()


    if request.user.username == "21bcs3000":
        data= {
        "projects": queryset,
        "username": request.user.username,
        }
        return render(request,"rs/view_projects_rspc.html", context= data)

    queryset= projects.objects.filter(project_investigator_id__username= request.user.username)
   
    data= {
        "projects": queryset,
        "username": request.user.username,
    }
    print(data)

    print(request.user.username)

    return render(request,"rs/view_projects_rspc.html", context= data)

def view_requests(request,id):
        
    if id== '1':
        queryset= requests.objects.filter(request_type= "staff")
    elif id== '0':
        if request.user.username == "21bcs3000" :
            queryset= rspc_inventory.objects.all()
            data= {
            "requests": queryset,
            "username": request.user.username
            }   
            return render(request,"rs/view_requests.html", context= data)
        
           
        queryset= rspc_inventory.objects.filter(project_investigator_id = request.user.username )
    else:
        render(request,"/404.html")

    data= {
        "requests": queryset,
        "username": request.user.username,
        "id":id,
    }

    # print(data)
    print(request.user.username)

    return render(request,"rs/view_requests.html", context= data)

def view_financial_outlay(request,pid):

    table_data=financial_outlay.objects.filter(project_id=pid).order_by('category', 'sub_category')

    years = set(table_data.values_list('year', flat=True))

    category_data = {}
    for category in table_data.values_list('category', flat=True).distinct():
        category_data[category] = table_data.filter(category=category)


    data = {
        'table_title': 'Total Budget Outlay',
        'table_caption': '...',  # Add caption if needed
        'years': list(years),
        'category_data': category_data,
    }

    print(data)
    return render(request,"rs/view_financial_outlay.html", context= data)

def submit_closure_report(request,id):
    id= int(id)
    obj= projects.objects.get(project_id=id)
    obj.status= 1; 
    obj.save()

    queryset= projects.objects.filter(project_investigator_id = request.user.username)

    print(queryset)
    
    data= {
        "projects": queryset,
        "username": request.user.username
    }
    messages.success(request,"Closure report submitted successfully")
    return render(request,"rs/view_projects_rspc.html",context=data)

def view_project_inventory(request,pj_id):
    pj_id=int(pj_id)
    queryset= requests.objects.filter(project_id=pj_id,request_type="funds")


    print(queryset)
    
    data= {
        "requests": queryset,
        "username": request.user.username
    }
    return render(request,"rs/view_project_inventory.html",context=data)

def view_project_staff(request,pj_id):
    pj_id=int(pj_id)
    queryset= requests.objects.filter(project_id=pj_id,request_type="staff")


    print(queryset)
    
    data= {
        "requests": queryset,
        "username": request.user.username
    }
    return render(request,"rs/view_project_staff.html",context=data)

def projectss(request):
    return render(request,"rs/projects.html")

def view_project_info(request,id):
    id= int(id)
    obj= projects.objects.get(project_id=id)



    data = {
        "project": obj,
    }
    
    return render(request,"rs/view_project_info.html", context= data)

def financial_outlay_form(request,pid):
    pid= int(pid)
    project= projects.objects.get(project_id=pid);
    categories = category.objects.all().distinct();

    categories_with_subcategories = category.objects.values('category_name', 'sub_category_name')

    # Organize the data into a dictionary
    category_subcategory_map = {}
    for item in categories_with_subcategories:
        category_name = item['category_name']
        subcategory = item['sub_category_name']
        if category_name in category_subcategory_map:
            category_subcategory_map[category_name].append(subcategory)
        else:
            category_subcategory_map[category_name] = [subcategory]

    # Pass the organized data to the template
    
    data = {
       "project_id": project.project_id,
       "years": list(range(1, int(project.years) + 1)),
       "category_subcategory_map": category_subcategory_map
       
    }

    return render(request,"rs/add_financial_outlay.html", context= data)



def add_staff_details(request , pid):
    if request.method == 'POST':
        obj = request.POST
        print("MG bro")
        print(obj)
        for key, value in obj.items():
            if key.startswith('staff'):                
                year_count = key.split('-')[-2]
                staff_count = key.split('-')[-1]
                # subcategory_key = f'subcategory-select-{year_count}-{category_count}'
                
                 # the table name is staff_allocations, and fileds are staff_allocation_id, project_id, staff_id, staff_name, qualification,year, stipend
                staff_id_key = f'staff_id-{year_count}-{staff_count}'    
                staff_name_key = f'staff_name-{year_count}-{staff_count}'
                qualification_key= f'qualification-{year_count}-{staff_count}'
                year = year_count
                stipend_key = f'stipend-{year_count}-{staff_count}'
                staff_id = obj.get(staff_id_key, [''])
                staff_name = obj.get(staff_name_key, [''])
                qualification = obj.get(qualification_key, [''])
                stipend = obj.get(stipend_key, [''])
                project_instance=projects.objects.get(project_id=pid)
                ob= staff_allocations.objects.all()

                if len(ob)==0 :
                    fid=1

                else :
                    fid= ob[0].staff_allocation_id+1
                
                staff_id_instance=User.objects.get(username=staff_id)   
                staff_allocations.objects.create(
                    staff_allocation_id=fid,
                    project_id=project_instance,
                    staff_id=staff_id_instance,
                    staff_name=staff_name,
                    qualification=qualification,
                    year=year,
                    stipend=stipend
                )
        
        return render(request,"rs/projects.html")


    project= projects.objects.get(project_id=pid);
    
    years_passed = int((datetime.datetime.now().date() - project.start_date).days / 365.25)
    
    data={
        "project_id":project.project_id,
        "years":list(range(1,int(project.years)+1)),
        "year":int(years_passed)+1,
    }
    
    return render(request,"rs/add_staff_details.html",context=data )



def add_financial_outlay(request,pid):
    if request.method == 'POST':
        
        project = projects.objects.get(project_id=pid)
        project.financial_outlay_status = 1
        project.save()
        
        obj = request.POST
        for key, value in obj.items():
            if key.startswith('category-select'):                
                year_count = key.split('-')[-2]
                category_count = key.split('-')[-1]
                subcategory_key = f'subcategory-select-{year_count}-{category_count}'
                amount_key = f'amount-{year_count}-{category_count}'

                category = value
                subcategory = obj.get(subcategory_key, [''])
                amount = obj.get(amount_key, [''])
                year = int(year_count)

                print(year)
                print(amount)
                print(subcategory)
                print(category)
                project_instance=projects.objects.get(project_id=pid)


                ob= financial_outlay.objects.all()
                if len(ob)==0 :
                    fid=1
                
                else :
                    fid= ob[0].financial_outlay_id+1
                financial_outlay.objects.create(
                    financial_outlay_id=fid,
                    project_id=project_instance,
                    category=category,
                    sub_category=subcategory,
                    amount=amount,
                    year=year,
                    status=0,
                    staff_limit=0
                )

    return render(request,"rs/projects.html")


# def add_financial_outlay(request):
#     if request.method == 'POST':
#         obj=request.POST
#         projectid = obj.get('project_id')
#         amount = obj.get('amount')
#         desc = obj.get('description')
#         check= projects.objects.filter(project_id=projectid)
#         if not check.exists():
#             messages.error(request,"Request not added, no such project exists")
#             return render(request,"rs/add_financial_outlay.html")

#         obj= financial_outlay.objects.all()
#         if len(obj)==0 :
#             requestid=1
            
#         else :
#             requestid= obj[0].request_id+1

#         financial_outlay.objects.create(
#             request_id=requestid,
#             project_id=projectid,
#             amount= amount,
#             description= desc
#         )
#         messages.success(request,"Financial outlay added successfully")
#         return redirect("/research_procedures")
#     return render(request,"rs/add_financial_outlay.html")
