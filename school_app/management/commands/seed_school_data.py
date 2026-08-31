from datetime import date

from django.core.management.base import BaseCommand

from results.models import Result
from school_app.models import (
    DownloadResource,
    Notice,
    Program,
    SiteSettings,
    Teacher,
)


class Command(BaseCommand):
    help = (
        'Restore missing school content (teachers, programs, notices, downloads, '
        'results). Safe to re-run: only creates records that do not already '
        'exist; never deletes or edits existing records.'
    )

    def handle(self, *args, **options):
        created = 0

        # ---------- Site settings polish ----------
        s = SiteSettings.objects.first()
        if s and s.address.strip().lower().startswith('panchkahapan'):
            s.address = 'Panchkhapan Municipality-7, Bihibare, Sankhuwasabha'
            s.save()
            self.stdout.write('SiteSettings.address polished')

        # ---------- Principal ----------
        if not Teacher.objects.filter(position__iexact='principal').exists():
            Teacher.objects.create(
                title='Kamal Bahadur Adhikari',
                slug='principal',
                position='Principal',
                department='management',
                qualification='M.Ed',
                photo='teachers/kamal adhikari.jpg',
                email='kamaladhikari435@gmail.com',
                phone='976100003',
                display_order=2,
                status=True,
                biography=(
                    'Mr. Kamal Bahadur Adhikari is a dedicated and experienced educational '
                    'leader committed to providing quality education, supporting teachers, '
                    'and creating a safe and inspiring learning environment.'
                ),
            )
            created += 1
            self.stdout.write(self.style.SUCCESS('Created Principal: Kamal Bahadur Adhikari'))

        # ---------- Teachers (photos already exist in media/teachers) ----------
        TEACHERS = [
            ('Chairperson of the School', 'Chairperson, School Management Committee', 'management',
             'M.Ed', 'teachers/head_management.jpg', 1),
            ('Bharat Bhattarai', 'Vice-Principal', 'management', 'M.Ed (English)',
             'teachers/Bharat Bhattarai.jpg', 3),
            ('Deepak Shrestha', 'Academic Coordinator', 'management', 'M.Ed (Curriculum & Evaluation)',
             'teachers/deepak shrestha.jpg', 4),
            ('Bhubhan Pandey', 'Secondary Mathematics Teacher', 'science', 'B.Sc. (Mathematics), B.Ed',
             'teachers/bhubhan pandey.jpg', 10),
            ('Shankar Basnet', 'Secondary Science Teacher', 'science', 'B.Sc. (Physics), B.Ed',
             'teachers/shankar basnet.jpg', 11),
            ('Manoj Ghimire', 'Computer Science Teacher', 'science', 'BCA (Computer Applications)',
             'teachers/manoj Ghimire.jpg', 12),
            ('Suga Rai', 'Secondary English Teacher', 'language', 'M.A. (English), B.Ed',
             'teachers/suga rai.jpg', 20),
            ('Binita Limbu', 'English & Grammar Teacher', 'language', 'B.A. (English), B.Ed',
             'teachers/binita limbu.jpg', 21),
            ('Indra Shrestha', 'Nepali Teacher', 'language', 'M.A. (Nepali), B.Ed',
             'teachers/indra shrestha.jpg', 22),
            ('Dhanahang Rai', 'Social Studies Teacher', 'social', 'B.A. (Social Studies), B.Ed',
             'teachers/dhanahang rai.jpg', 30),
            ('Tara Vurtel', 'Art & Social Studies Teacher', 'social', 'B.A., B.Ed',
             'teachers/tara vurtel.jpg', 31),
            ('Dipa Pariyar', 'Primary Level Teacher', 'primary', '10+2, ECD Training',
             'teachers/dipa pariyar.jpg', 40),
            ('Pabitra Tamang', 'Early Childhood Teacher', 'primary', '10+2, Montessori Training',
             'teachers/pabitra tamang.jpg', 41),
            ('Rajesh Basent', 'Physical Education Teacher', 'sports', 'B.Ed (Health & Physical Education)',
             'teachers/rajesh basent.jpg', 50),
        ]
        for title, position, dept, qual, photo, order in TEACHERS:
            if Teacher.objects.filter(title__iexact=title).exists():
                continue
            Teacher.objects.create(
                title=title, position=position, department=dept,
                qualification=qual, photo=photo,
                biography='Dedicated member of the staff of Shree Jaljala Secondary School.',
                display_order=order, status=True,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created Teacher: {title}'))


        # ---------- Programs ----------
        PROGRAMS = [
            ('Secondary Education (Grades 9 - 10)', '2 Years', 'As per school policy / Contact School',
             'Grade 8 completion (Basic Level)', 'programs/program_1.png', 4),
            ('Early Childhood Development (Nursery - KG)', '3 Years', 'Free (Government School)',
             'Children aged 3 to 5 years', 'programs/image 14.jpg', 1),
            ('Primary Level (Grades 1 - 5)', '5 Years', 'Free (Government School)',
             'Grade 1 admission (age 5+)', 'programs/image 4.jpg', 2),
            ('Basic Level (Grades 6 - 8)', '3 Years', 'Free (Government School)',
             'Grade 5 completion', 'programs/image 6.jpg', 3),
        ]
        for name, dur, fee, elig, img, order in PROGRAMS:
            if Program.objects.filter(title__iexact=name).exists():
                continue
            Program.objects.create(
                title=name, duration=dur, fee=fee, eligibility=elig, image=img,
                display_order=order, status=True,
                description=(
                    'Shree Jaljala Secondary School delivers the National Curriculum of Nepal '
                    'for this level with qualified teachers, continuous assessment, and '
                    'co-curricular activities that build confidence alongside academics. '
                    'Students take part in house competitions, morning assembly activities, '
                    'and practical classes in our science and computer labs.'
                ),
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created Program: {name}'))

        # ---------- Notices ----------
        NOTICES = [
            ('Admission Open for Academic Session 2083 B.S.', 'admission',
             'Applications are open for admission to Class Nursery up to Class 10 for the '
             'academic session 2083 B.S. Parents/guardians may collect the admission form from '
             'the school office or apply online through the Admission page. For details, '
             'contact the school office during office hours.'),
            ('First Terminal Examination Routine Published', 'exam',
             'The First Terminal Examination for all classes from Grade 1 to Grade 10 will '
             'begin as per the published routine. Students are advised to check the exam '
             'routine on the Downloads page and reach the examination hall 15 minutes early '
             'with their admit cards.'),
            ('School Closed on Public Holiday', 'general',
             'Dear parents and students, please be informed that the school will remain closed '
             'on account of the public holiday. Regular classes will resume from the next '
             'working day as per the academic calendar.'),
        ]
        for title, cat, desc in NOTICES:
            if Notice.objects.filter(title__iexact=title).exists():
                continue
            Notice.objects.create(title=title, description=desc, category=cat, status=True)
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created Notice: {title}'))

        # ---------- Downloads ----------
        DOWNLOADS = [
            ('Admission Application Form 2083', 'form', 'PDF, 220 KB', 1),
            ('Academic Calendar 2083 B.S.', 'routine', 'PDF, 1.2 MB', 5),
            ('SEE Syllabus & Curriculum (Class 9-10)', 'syllabus', 'PDF, 3.5 MB', 1),
        ]
        for name, cat, size, order in DOWNLOADS:
            if DownloadResource.objects.filter(title__iexact=name).exists():
                continue
            DownloadResource.objects.create(
                title=name, category=cat, file='downloads/schoolnotices.png',
                file_size=size, display_order=order, status=True,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created Download: {name}'))

        # ---------- Results ----------
        RESULTS = [
            ('First Terminal Examination 2082 - Class 10', 'First Terminal Examination',
             '10', '2082', date(2082, 6, 1)),
            ('SEE Board Examination 2081 - Results', 'SEE Board Examination',
             '10', '2081', date(2025, 3, 15)),
        ]
        for title, exam, cls, year, pub in RESULTS:
            if Result.objects.filter(title__iexact=title).exists():
                continue
            Result.objects.create(
                title=title, examination=exam, class_name=cls, academic_year=year,
                result_file='results/exam.jpg', published_date=pub,
                description='Official published result. Download the mark-sheet summary or '
                            'contact the school office for details.',
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created Result: {title}'))

        self.stdout.write(self.style.SUCCESS(f'Done. {created} record(s) created.'))
        self.stdout.write(
            f'Teachers: {Teacher.objects.count()} | Programs: {Program.objects.count()} '
            f'| Notices: {Notice.objects.count()} | Downloads: {DownloadResource.objects.count()} '
            f'| Results: {Result.objects.count()}'
        )
