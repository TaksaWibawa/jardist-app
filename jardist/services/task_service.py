from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from itertools import groupby
from jardist.decorators import login_and_group_required
from jardist.forms.material_form import MaterialForm
from jardist.forms.sub_task_material_form import SubTaskMaterialFormSet
from jardist.models.task_models import Task, SubTask, SubTaskMaterial, TaskDocumentation
from jardist.utils import int_to_roman
import xlsxwriter

def add_material(request, task_id, redirect_url, context='rab'):
    task = Task.objects.get(id=task_id)
    material_form = MaterialForm(request.POST or None, task=task, context=context)

    if request.method == 'POST':
        if material_form.is_valid():
            material_form.save()
            messages.success(request, 'Data berhasil disimpan')
            return JsonResponse({'error': False})
        else:
            form_errors = material_form.errors.as_json()
            return JsonResponse({'error': True, 'form_errors': form_errors})
    return redirect(redirect_url, task_id=task.id)

@login_and_group_required('Staff')
def AddRABMaterial(request, task_id):
    return add_material(request, task_id, 'edit_task_material', 'rab')

@login_and_group_required('Staff', 'Pengawas')
def AddRealizationMaterial(request, task_id):
    return add_material(request, task_id, 'update_realization_task_material', 'realization')

def get_sub_tasks_materials_by_category(task, sort_by='', search=''):
    sub_tasks_materials_by_category = {}
    sub_task_materials = SubTaskMaterial.objects.filter(subtask__task=task, material__name__icontains=search).order_by('-subtask').select_related('subtask', 'material', 'category')
    sub_task_materials_by_sub_task = {sub_task: list(stms) for sub_task, stms in groupby(sub_task_materials, key=lambda x: x.subtask)}

    def has_volume_changed(current_client_volume, previous_client_volume, current_contractor_volume, previous_contractor_volume):
        return current_client_volume != previous_client_volume or current_contractor_volume != previous_contractor_volume

    for sub_task, stms in sub_task_materials_by_sub_task.items():
        materials_by_category = {}
        for stm in stms:
            material = stm.material

            if sort_by == 'realization':
                material.client_volume = stm.realization_client_volume
                material.contractor_volume = stm.realization_contractor_volume
            elif sort_by == 'rab':
                material.client_volume = stm.rab_client_volume
                material.contractor_volume = stm.rab_contractor_volume
            else:
                material.rab_client_volume = stm.rab_client_volume
                material.rab_contractor_volume = stm.rab_contractor_volume
                material.realization_client_volume = stm.realization_client_volume
                material.realization_contractor_volume = stm.realization_contractor_volume

            material.has_volume_changed = has_volume_changed(stm.realization_client_volume, stm.rab_client_volume, stm.realization_contractor_volume, stm.rab_contractor_volume)

            material.labor_price = stm.labor_price or 0
            material.category = stm.category
            material.price = stm.material_price or 0
            material.is_additional = stm.is_additional
            materials_by_category.setdefault(stm.category, []).append(material)

        sorted_materials_by_category = {}
        if sort_by in ['rab', 'realization']:
            for category in sorted(materials_by_category.keys(), key=lambda x: 0 if x.name == 'Material Utama' else 1 if x.name == 'Material Non Utama' else 2 if x.name == 'Lain - Lain' else 3):
                sorted_materials = sorted(materials_by_category[category], key=lambda x: (-x.client_volume if x.client_volume is not None else 0, -x.contractor_volume if x.contractor_volume is not None else 0, x.name))
                sorted_materials_by_category[category] = sorted_materials
        else:
            for category in sorted(materials_by_category.keys(), key=lambda x: 0 if x.name == 'Material Utama' else 1 if x.name == 'Material Non Utama' else 2 if x.name == 'Lain - Lain' else 3):
                for material in materials_by_category[category]:
                    material.combined_volume = material.rab_client_volume or 0 + material.rab_contractor_volume or 0 + material.realization_client_volume or 0 + material.realization_contractor_volume or 0
                
                sorted_materials = sorted(materials_by_category[category], key=lambda x: (-x.combined_volume, x.name))
                sorted_materials_by_category[category] = sorted_materials

        sub_tasks_materials_by_category[sub_task] = sorted_materials_by_category

    return sub_tasks_materials_by_category

def create_subtask_material_formsets(request, task, sort_by):
    search = request.GET.get('search', '')
    sub_tasks_materials_by_category = get_sub_tasks_materials_by_category(task, sort_by=sort_by, search=search)
    formsets = {}
    formsets_data = []

    for sub_task, materials_by_category in sub_tasks_materials_by_category.items():
        formsets[sub_task] = {}
        for category, materials in materials_by_category.items():
            material_formsets = []
            for material in materials:
                queryset = SubTaskMaterial.objects.filter(subtask=sub_task, material=material)
                formset_initial_data = [
                    {
                        f'{sort_by}_client_volume': getattr(stm, f'{sort_by}_client_volume', stm.rab_client_volume) or 0,
                        f'{sort_by}_contractor_volume': getattr(stm, f'{sort_by}_contractor_volume', stm.rab_contractor_volume) or 0
                    } 
                    for stm in queryset
                ]
                formset = SubTaskMaterialFormSet(
                    request.POST or None,
                    queryset=queryset,
                    initial=formset_initial_data,
                    show_type=sort_by,
                    prefix=f'{sub_task}_{category}_{material.id}'
                )
                material_formsets.append((material, formset))
            
            formsets[sub_task][category] = material_formsets
            formsets_data.extend(material_formsets)

    return formsets, formsets_data

def get_task_data(request):
    pk = request.GET.get('pk')
    tasks = Task.objects.filter(pk_instance=pk).values('id', 'task_name')
    return JsonResponse(list(tasks), safe=False)

@login_and_group_required()
def download_pk_material_details(request, pk_id):
    try:
        tasks = Task.objects.filter(pk_instance__id=pk_id)
    except Task.DoesNotExist:
        return HttpResponse('Data not found', status=404)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{tasks[0].pk_instance.pk_number}_{timezone.localdate()}_laporan_realisasi_material.xlsx"'

    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    bold_format = workbook.add_format({'bold': True})
    merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True})
    header_format = workbook.add_format({'bold': True, 'top': 6, 'bottom': 6, 'left': 1, 'right': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    sub_header_format_top = workbook.add_format({'bold': True, 'top': 6, 'bottom': 1, 'left': 1, 'right': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    sub_header_format_bottom = workbook.add_format({'bold': True, 'top': 1, 'bottom': 6, 'left': 1, 'right': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})

    cell_formats = {
        'empty': workbook.add_format({'left': 1, 'right': 1}),
        'middle': workbook.add_format({'left': 1, 'right': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
        'left': workbook.add_format({'left': 1, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True}),
        'right': workbook.add_format({'left': 1, 'right': 1, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True}),
        'middle_last_row': workbook.add_format({'left': 1, 'right': 1, 'bottom': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
        'left_last_row': workbook.add_format({'left': 1, 'right': 1, 'bottom': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True}),
        'right_last_row': workbook.add_format({'left': 1, 'right': 1, 'bottom': 1, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True}),
        'left_bold': workbook.add_format({'left': 1, 'right': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'bold': True}),
        'right_bold': workbook.add_format({'left': 1, 'right': 1, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True, 'bold': True}),
        'middle_bold': workbook.add_format({'left': 1, 'right': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True}),
    }

    def write_headers(worksheet):
        headers = ['NO', 'JENIS MATERIAL', 'SATUAN', 'VOLUME RENCANA PLN', 'VOLUME RENCANA PEMB.', 'VOLUME REALISASI PLN', 'VOLUME REALISASI PEMB.', 'KETERANGAN', 'SELISIH']
        worksheet.merge_range('A1:I1', 'LAPORAN REALISASI MATERIAL', merge_format)
        details = ['Pekerjaan', '', 'Lokasi', 'Nomor PK', 'Nomor SPK']
        for i, detail in enumerate(details):
            worksheet.merge_range(f'A{3 + i}:B{3 + i}', detail, bold_format)

        worksheet.merge_range('A9:A10', headers[0], header_format)
        worksheet.merge_range('B9:B10', headers[1], header_format)
        worksheet.merge_range('C9:C10', headers[2], header_format)
        worksheet.merge_range('D9:E9', 'VOLUME RENCANA', sub_header_format_top)
        worksheet.write('D10', headers[3].split()[-1], sub_header_format_bottom)
        worksheet.write('E10', headers[4].split()[-1], sub_header_format_bottom)
        worksheet.merge_range('F9:G9', 'VOLUME REALISASI', sub_header_format_top)
        worksheet.write('F10', headers[5].split()[-1], sub_header_format_bottom)
        worksheet.write('G10', headers[6].split()[-1], sub_header_format_bottom)
        worksheet.merge_range('H9:H10', headers[7], header_format)
        worksheet.merge_range('I9:I10', headers[8], header_format)

    def write_task_details(worksheet, task, row_num):
        details = [task.task_name, f'Atas Nama {task.customer_name}', task.location, task.pk_instance.pk_number, task.pk_instance.spk.spk_number]
        for i, value in enumerate(details):
            worksheet.merge_range(f'C{3 + i}:I{3 + i}', f': {value}')
        return row_num + 9

    def write_subtask_header(worksheet, row_num):
        for col in range(7):
            worksheet.write(row_num, col, chr(65 + col), header_format)
        for col in range(7, 9):
            worksheet.write(row_num, col, "", header_format)
        
        row_num += 1

        for col in range(9):
            worksheet.write(row_num, col, '', cell_formats['empty'])

        row_num += 1
        return row_num
    
    def calculate_status_and_difference(rab_client_volume, realization_client_volume, rab_contractor_volume, realization_contractor_volume):
        if rab_client_volume != realization_client_volume:
            status = "KTK"
            difference = realization_client_volume - rab_client_volume
        elif rab_client_volume != realization_contractor_volume or rab_contractor_volume != realization_client_volume:
            status = "Pengadaan"
            difference = (realization_contractor_volume - rab_client_volume) if rab_client_volume != realization_contractor_volume else (realization_client_volume -    rab_contractor_volume)
        else:
            status = ""
            difference = ""

        return status, difference

    def write_subtask_materials(worksheet, subtask, row_num, subtask_counter, cell_formats, is_last_subtask):
        worksheet.write(row_num, 0, chr(subtask_counter), cell_formats['middle_bold'])
        worksheet.write(row_num, 1, subtask.sub_task_type.name.upper(), cell_formats['left_bold'])
        for col in range(2, 9):
            worksheet.write(row_num, col, '', cell_formats['empty'])
        row_num += 1

        materials_by_category = {}
        for subtask_material in subtask.subtaskmaterial_set.all():
            category = subtask_material.category.name
            if category not in materials_by_category:
                materials_by_category[category] = []
            materials_by_category[category].append(subtask_material)

        roman_num = 1
        categories_processed = 0
        total_categories = len(materials_by_category)
        for category, materials in materials_by_category.items():
            worksheet.write(row_num, 0, int_to_roman(roman_num), cell_formats['middle_bold'])
            worksheet.write(row_num, 1, category.upper(), cell_formats['left_bold'])
            for col in range(2, 9):
                worksheet.write(row_num, col, '', cell_formats['empty'])
            row_num += 1
            roman_num += 1

            material_counter = 1
            total_materials = len(materials)
            for i, subtask_material in enumerate(materials):
                material = subtask_material.material
                is_last_material = (i == total_materials - 1) and is_last_subtask
                format_suffix = '_last_row' if is_last_material else ''

                status, difference = calculate_status_and_difference(subtask_material.rab_client_volume, subtask_material.realization_client_volume, subtask_material.rab_contractor_volume, subtask_material.realization_contractor_volume)

                worksheet.write(row_num, 0, material_counter, cell_formats['middle' + format_suffix])
                worksheet.write(row_num, 1, material.name.upper(), cell_formats['left' + format_suffix])
                worksheet.write(row_num, 2, material.unit, cell_formats['middle' + format_suffix])
                worksheet.write(row_num, 3, subtask_material.rab_client_volume, cell_formats['right' + format_suffix])
                worksheet.write(row_num, 4, subtask_material.rab_contractor_volume, cell_formats['right' + format_suffix])
                worksheet.write(row_num, 5, subtask_material.realization_client_volume, cell_formats['right' + format_suffix])
                worksheet.write(row_num, 6, subtask_material.realization_contractor_volume, cell_formats['right' + format_suffix])
                worksheet.write(row_num, 7, status, cell_formats['middle' + format_suffix])
                worksheet.write(row_num, 8, difference, cell_formats['right' + format_suffix])
                row_num += 1
                material_counter += 1

            categories_processed += 1
            if categories_processed <= total_categories:
                for _ in range(2):
                    if is_last_subtask and categories_processed == total_categories:
                        break
                    for col in range(9):
                        worksheet.write(row_num, col, '', cell_formats['empty'])
                    row_num += 1

            if not is_last_subtask or categories_processed < total_categories:
                for col in range(9):
                    worksheet.write(row_num, col, '', cell_formats['empty'])
                row_num += 1

        return row_num
    
    task_counter = 1
    for task in tasks:
        subtasks = list(SubTask.objects.filter(task=task).prefetch_related('subtaskmaterial_set__material'))
        worksheet_name = f"{task.task_name[:27]}_{task_counter}"
        worksheet = workbook.add_worksheet(name=worksheet_name)
        write_headers(worksheet)
        row_num = write_task_details(worksheet, task, 1)
        row_num = write_subtask_header(worksheet, row_num)

        subtask_counter = 65
        for subtask in subtasks:
            is_last_subtask = subtask == subtasks[-1]
            row_num = write_subtask_materials(worksheet, subtask, row_num, subtask_counter, cell_formats, is_last_subtask)
            subtask_counter += 1

        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:C', 5)
        worksheet.set_column('D:E', 10)
        worksheet.set_column('F:G', 10)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 10)

        worksheet.freeze_panes(11, 0)

        task_counter += 1

    workbook.close()
    return response

# it will only fetch one instance task documentation which have one location and multiple documentation
@login_and_group_required()
def get_task_documentation(request):
    task_id = request.GET.get('task_id')
    task_documentations = TaskDocumentation.objects.filter(task_id=task_id).values('id', 'location', 'photos')
    return JsonResponse(list(task_documentations), safe=False)