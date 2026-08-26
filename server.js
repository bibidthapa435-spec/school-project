import express from 'express';
import nunjucks from 'nunjucks';
import path from 'path';
import fs from 'fs';
import multer from 'multer';
import { fileURLToPath } from 'url';
import { schoolData, departmentChoices, noticeCategoryChoices, galleryCategoryChoices, slugify } from './src/data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Ensure upload directories exist
const uploadDirs = [
  'media/uploads',
  'media/slider',
  'media/logo',
  'media/teachers',
  'media/gallery',
  'media/notices',
  'media/programs'
];
uploadDirs.forEach(dir => {
  const fullPath = path.join(__dirname, dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
  }
});

// Multer Storage Configuration for File Uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, 'media/uploads'));
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname) || '.jpg';
    cb(null, file.fieldname + '-' + uniqueSuffix + ext);
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Helper function to resolve uploaded image or fall back to static path
function resolveImageUrl(req, fileFieldName, urlFieldName, fallbackUrl) {
  if (req.file) {
    return `/media/uploads/${req.file.filename}`;
  }
  if (req.files && req.files[fileFieldName] && req.files[fileFieldName][0]) {
    return `/media/uploads/${req.files[fileFieldName][0].filename}`;
  }
  if (req.body && req.body[urlFieldName] && req.body[urlFieldName].trim() !== '') {
    return req.body[urlFieldName].trim();
  }
  return fallbackUrl;
}

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Serve static files and media uploads
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use('/media', express.static(path.join(__dirname, 'media')));

// View engine setup using Nunjucks (Django-compatible syntax)
const nunjucksEnv = nunjucks.configure(path.join(__dirname, 'templates'), {
  autoescape: true,
  express: app,
  noCache: true
});

// Custom tag extension for Django {% load ... %}
nunjucksEnv.addExtension('LoadTag', new (function() {
  this.tags = ['load'];
  this.parse = function(parser, nodes) {
    var tok = parser.nextToken();
    var args = parser.parseSignature(null, true);
    parser.advanceAfterBlockEnd(tok.value);
    return new nodes.CallExtension(this, 'run', args, []);
  };
  this.run = function() { return ''; };
})());

// Custom tag extension for Django {% csrf_token %}
nunjucksEnv.addExtension('CsrfTag', new (function() {
  this.tags = ['csrf_token'];
  this.parse = function(parser, nodes) {
    var tok = parser.nextToken();
    parser.advanceAfterBlockEnd(tok.value);
    return new nodes.CallExtension(this, 'run', null, []);
  };
  this.run = function() { return ''; };
})());

app.set('view engine', 'html');

// Global middleware for local template variables
app.use((req, res, next) => {
  const settings = schoolData.settings || {
    school_name: "Shree Jaljala Secondary School",
    tagline: "Quality Education for a Brighter Future",
    logo_url: "/static/images/logo.png",
    phone: "+977-9842000000 / +977-9800000000",
    email: "info@shreejaljala.edu.np",
    address: "Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Nepal",
    estd: "2045 B.S.",
    facebook_url: "https://facebook.com",
    youtube_url: "https://youtube.com"
  };

  res.locals.schoolSettings = settings;
  res.locals.SCHOOL_NAME = settings.school_name;
  res.locals.SCHOOL_ADDRESS = settings.address;
  res.locals.SCHOOL_PHONE = settings.phone;
  res.locals.SCHOOL_EMAIL = settings.email;
  res.locals.SCHOOL_ESTD = settings.estd;
  res.locals.FACEBOOK_URL = settings.facebook_url;
  res.locals.INSTAGRAM_URL = "https://instagram.com";
  res.locals.YOUTUBE_URL = settings.youtube_url;
  res.locals.MARQUEE_NOTICES = schoolData.notices;
  res.locals.user = null;
  res.locals.path = req.path;
  res.locals.messages = [];
  res.locals.showPreloader = false;
  next();
});

// Home Page
app.get('/', (req, res) => {
  const principal = schoolData.teachers.find(t => t.position === 'Principal') || schoolData.teachers[0];
  const nowStr = new Date().toISOString().split('T')[0];
  const activePopups = (schoolData.popups || []).filter(p => {
    if (p.is_active === false) return false;
    if (p.start_date && p.start_date > nowStr) return false;
    if (p.end_date && p.end_date < nowStr) return false;
    return true;
  });
  const activePopup = activePopups.length > 0 ? activePopups[0] : null;

  res.render('home/index', {
    title: 'Shree Jaljala Secondary School | Panchkhapan, Sankhuwasabha',
    sliders: schoolData.sliders,
    principal: principal,
    programs: schoolData.programs,
    notices: schoolData.notices.slice(0, 3),
    teachers: schoolData.teachers.slice(0, 4),
    gallery_items: schoolData.gallery.slice(0, 8),
    testimonials: schoolData.testimonials,
    activePopup: activePopup,
    activePopups: activePopups,
    showPreloader: true
  });
});

// About Us
app.get('/about', (req, res) => {
  res.render('pages/about', { title: 'About Us | Jaljala Secondary School' });
});

// Principal Message
app.get('/principal-message', (req, res) => {
  const principal = schoolData.teachers.find(t => t.position === 'Principal') || schoolData.teachers[0];
  res.render('pages/principal_message', {
    title: "Principal's Message | Jaljala Secondary School",
    principal: principal
  });
});

// Facilities
app.get('/facilities', (req, res) => {
  res.render('pages/facilities', { title: 'Infrastructure & Facilities | Jaljala Secondary School' });
});

// Online Admission Form
app.get('/admission', (req, res) => {
  res.render('pages/admission', { title: 'Online Student Admission Application | Jaljala Secondary School' });
});

app.post('/admission', (req, res) => {
  const newAdmission = {
    id: Date.now(),
    student_name: req.body.student_name || req.body.name,
    parent_name: req.body.parent_name,
    class_applying: req.body.class_applying || req.body.grade,
    phone: req.body.phone,
    address: req.body.address,
    status: 'Pending Review',
    created_at: new Date()
  };
  schoolData.admissions.push(newAdmission);
  res.render('pages/admission', {
    title: 'Online Student Admission Application | Jaljala Secondary School',
    messages: [{ tags: 'success', text: 'Your admission application has been submitted successfully! The school administration office will contact you soon.' }]
  });
});

// Contact Us
app.get('/contact', (req, res) => {
  res.render('pages/contact', { title: 'Contact Us & Location | Jaljala Secondary School' });
});

app.post('/contact', (req, res) => {
  const newMsg = {
    id: Date.now(),
    name: req.body.name,
    email: req.body.email,
    subject: req.body.subject,
    message: req.body.message,
    created_at: new Date()
  };
  schoolData.contacts.push(newMsg);
  res.render('pages/contact', {
    title: 'Contact Us & Location | Jaljala Secondary School',
    messages: [{ tags: 'success', text: 'Thank you for reaching out! Your message has been received by the school administration.' }]
  });
});

// Academic Programs
app.get('/programs', (req, res) => {
  res.render('programs/program_list', {
    title: 'Academic Programs & Curriculum | Jaljala Secondary School',
    programs: schoolData.programs
  });
});

app.get('/programs/:slug', (req, res) => {
  const program = schoolData.programs.find(p => p.slug === req.params.slug) || schoolData.programs[0];
  res.render('programs/program_detail', {
    title: `${program.name} | Jaljala Secondary School`,
    program: program
  });
});

// Teachers & Staff
app.get('/teachers', (req, res) => {
  res.render('teacher/teacher_list', {
    title: 'Faculty & Administration | Jaljala Secondary School',
    teachers: schoolData.teachers,
    departments: departmentChoices
  });
});

app.get('/teachers/:slug', (req, res) => {
  const teacher = schoolData.teachers.find(t => t.slug === req.params.slug) || schoolData.teachers[0];
  res.render('teacher/teacher_detail', {
    title: `${teacher.name} (${teacher.position}) | Jaljala Secondary School`,
    teacher: teacher
  });
});

// Photo Gallery
app.get('/gallery', (req, res) => {
  const category = req.query.category || '';
  let items = schoolData.gallery;
  if (category) {
    items = items.filter(i => i.category === category);
  }
  res.render('gallery/gallery_list', {
    title: 'Photo Gallery & Events | Jaljala Secondary School',
    gallery_items: items,
    categories: galleryCategoryChoices,
    selected_category: category
  });
});

// Downloads Resource Center
app.get('/downloads', (req, res) => {
  res.render('pages/downloads', {
    title: 'Downloadable Resources, Forms & Calendar | Jaljala Secondary School',
    downloads: schoolData.downloads
  });
});

// Notices & Announcements
app.get('/notices', (req, res) => {
  const query = req.query.q ? req.query.q.toLowerCase() : '';
  const category = req.query.category || '';
  let noticesList = schoolData.notices;

  if (category) {
    noticesList = noticesList.filter(n => n.category === category);
  }
  if (query) {
    noticesList = noticesList.filter(n =>
      n.title.toLowerCase().includes(query) ||
      n.description.toLowerCase().includes(query)
    );
  }

  res.render('notice/notice_list', {
    title: 'Notices & Announcements | Jaljala Secondary School',
    page_obj: noticesList,
    categories: noticeCategoryChoices,
    selected_category: category,
    query: req.query.q || ''
  });
});

app.get('/notices/:slug', (req, res) => {
  const notice = schoolData.notices.find(n => n.slug === req.params.slug) || schoolData.notices[0];
  const recent = schoolData.notices.filter(n => n.id !== notice.id).slice(0, 4);
  res.render('notice/notice_detail', {
    title: `${notice.title} | Jaljala Secondary School Notice`,
    notice: notice,
    recent_notices: recent
  });
});

// Auth Stubs
app.post('/login', (req, res) => { res.redirect('/'); });
app.post('/register', (req, res) => { res.redirect('/'); });
app.get('/logout', (req, res) => { res.redirect('/'); });

// ADMIN PORTAL - DYNAMIC DASHBOARD & CONTENT MANAGEMENT
app.get('/admin', (req, res) => {
  const activeTab = req.query.tab || 'dashboard';
  const successMsg = req.query.msg || null;

  res.render('admin/admin_dashboard', {
    layout: false,
    activeTab: activeTab,
    successMsg: successMsg,
    schoolSettings: schoolData.settings,
    schoolData: schoolData,
    departmentChoices: departmentChoices,
    noticeCategoryChoices: noticeCategoryChoices,
    galleryCategoryChoices: galleryCategoryChoices
  });
});

// ADMIN POST ENDPOINTS - SCHOOL SETTINGS & LOGO
app.post('/admin/settings/update', upload.single('logo_file'), (req, res) => {
  const logoUrl = resolveImageUrl(req, 'logo_file', 'logo_url', schoolData.settings.logo_url);
  
  schoolData.settings.school_name = req.body.school_name || schoolData.settings.school_name;
  schoolData.settings.tagline = req.body.tagline || schoolData.settings.tagline;
  schoolData.settings.logo_url = logoUrl;
  schoolData.settings.phone = req.body.phone || schoolData.settings.phone;
  schoolData.settings.email = req.body.email || schoolData.settings.email;
  schoolData.settings.address = req.body.address || schoolData.settings.address;
  schoolData.settings.facebook_url = req.body.facebook_url || schoolData.settings.facebook_url;
  schoolData.settings.youtube_url = req.body.youtube_url || schoolData.settings.youtube_url;

  res.redirect('/admin?tab=settings&msg=' + encodeURIComponent('School logo and settings updated successfully!'));
});

// ADMIN POST ENDPOINTS - SLIDERS (Add, Edit, Delete)
app.post('/admin/slider/add', upload.single('image_file'), (req, res) => {
  const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', '/static/images/slider1.jpg');
  const newSlider = {
    id: Date.now(),
    title: req.body.title || 'Welcome to Shree Jaljala Secondary School',
    subtitle: req.body.subtitle || '',
    description: req.body.description || '',
    button_text: req.body.button_text || 'Learn More',
    button_url: req.body.button_url || '/about',
    image: { url: imageUrl },
    overlay_color: '#0b1b2b',
    overlay_opacity: 0.5,
    display_order: schoolData.sliders.length + 1,
    status: true
  };
  schoolData.sliders.push(newSlider);
  res.redirect('/admin?tab=sliders&msg=' + encodeURIComponent('New homepage slider added successfully!'));
});

app.post('/admin/slider/edit/:id', upload.single('image_file'), (req, res) => {
  const id = parseInt(req.params.id);
  const slider = schoolData.sliders.find(s => s.id === id);
  if (slider) {
    const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', slider.image ? slider.image.url : '/static/images/slider1.jpg');
    slider.title = req.body.title || slider.title;
    slider.subtitle = req.body.subtitle !== undefined ? req.body.subtitle : slider.subtitle;
    slider.description = req.body.description !== undefined ? req.body.description : slider.description;
    slider.button_text = req.body.button_text || slider.button_text;
    slider.button_url = req.body.button_url || slider.button_url;
    slider.image = { url: imageUrl };
  }
  res.redirect('/admin?tab=sliders&msg=' + encodeURIComponent('Slider updated successfully!'));
});

app.post('/admin/slider/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.sliders = schoolData.sliders.filter(s => s.id !== id);
  res.redirect('/admin?tab=sliders&msg=' + encodeURIComponent('Slider deleted successfully!'));
});

// ADMIN POST ENDPOINTS - TEACHERS (Add, Edit, Delete)
app.post('/admin/teacher/add', upload.single('photo_file'), (req, res) => {
  const photoUrl = resolveImageUrl(req, 'photo_file', 'photo_url', '/static/images/principal.jpg');
  const deptChoice = departmentChoices.find(d => d[0] === req.body.department);
  const newTeacher = {
    id: Date.now(),
    name: req.body.name,
    slug: slugify(req.body.name),
    position: req.body.position,
    department: req.body.department,
    department_display: deptChoice ? deptChoice[1] : req.body.department,
    qualification: req.body.qualification || 'Qualified Educator',
    photo: { url: photoUrl },
    phone: req.body.phone || '9842000000',
    email: req.body.email || `${slugify(req.body.name)}@jaljala.edu.np`,
    biography: req.body.biography || 'Dedicated faculty member of Shree Jaljala Secondary School.',
    display_order: schoolData.teachers.length + 1,
    status: true
  };
  schoolData.teachers.push(newTeacher);
  res.redirect('/admin?tab=teachers&msg=' + encodeURIComponent('Teacher added successfully!'));
});

app.post('/admin/teacher/edit/:id', upload.single('photo_file'), (req, res) => {
  const id = parseInt(req.params.id);
  const teacher = schoolData.teachers.find(t => t.id === id);
  if (teacher) {
    const photoUrl = resolveImageUrl(req, 'photo_file', 'photo_url', teacher.photo ? teacher.photo.url : '/static/images/principal.jpg');
    const deptChoice = departmentChoices.find(d => d[0] === req.body.department);
    teacher.name = req.body.name || teacher.name;
    teacher.slug = slugify(teacher.name);
    teacher.position = req.body.position || teacher.position;
    teacher.department = req.body.department || teacher.department;
    teacher.department_display = deptChoice ? deptChoice[1] : teacher.department;
    teacher.qualification = req.body.qualification || teacher.qualification;
    teacher.photo = { url: photoUrl };
    teacher.phone = req.body.phone || teacher.phone;
    teacher.email = req.body.email || teacher.email;
    teacher.biography = req.body.biography || teacher.biography;
  }
  res.redirect('/admin?tab=teachers&msg=' + encodeURIComponent('Teacher updated successfully!'));
});

app.post('/admin/teacher/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.teachers = schoolData.teachers.filter(t => t.id !== id);
  res.redirect('/admin?tab=teachers&msg=' + encodeURIComponent('Teacher deleted successfully!'));
});

// ADMIN POST ENDPOINTS - NOTICES (Add, Edit, Delete)
app.post('/admin/notice/add', upload.single('image_file'), (req, res) => {
  const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', '/static/images/image/schoolnotices.png');
  const catChoice = noticeCategoryChoices.find(c => c[0] === req.body.category);
  const newNotice = {
    id: Date.now(),
    title: req.body.title,
    slug: slugify(req.body.title),
    category: req.body.category,
    category_display: catChoice ? catChoice[1] : req.body.category,
    image: { url: imageUrl },
    description: req.body.description,
    featured: true,
    status: true,
    created_at: new Date()
  };
  schoolData.notices.unshift(newNotice);
  res.redirect('/admin?tab=notices&msg=' + encodeURIComponent('Notice published successfully!'));
});

app.post('/admin/notice/edit/:id', upload.single('image_file'), (req, res) => {
  const id = parseInt(req.params.id);
  const notice = schoolData.notices.find(n => n.id === id);
  if (notice) {
    const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', notice.image ? notice.image.url : '/static/images/image/schoolnotices.png');
    const catChoice = noticeCategoryChoices.find(c => c[0] === req.body.category);
    notice.title = req.body.title || notice.title;
    notice.slug = slugify(notice.title);
    notice.category = req.body.category || notice.category;
    notice.category_display = catChoice ? catChoice[1] : notice.category;
    notice.image = { url: imageUrl };
    notice.description = req.body.description || notice.description;
  }
  res.redirect('/admin?tab=notices&msg=' + encodeURIComponent('Notice updated successfully!'));
});

app.post('/admin/notice/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.notices = schoolData.notices.filter(n => n.id !== id);
  res.redirect('/admin?tab=notices&msg=' + encodeURIComponent('Notice deleted successfully!'));
});

// ADMIN POST ENDPOINTS - POPUP BANNERS (Add, Edit, Delete, Toggle)
app.post('/admin/popup/add', upload.single('image_file'), (req, res) => {
  if (!schoolData.popups) schoolData.popups = [];
  const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', '/media/notices/admission_notice.png');
  const newPopup = {
    id: Date.now(),
    title: req.body.title,
    subtitle: req.body.subtitle || '',
    description: req.body.description || req.body.message || '',
    message: req.body.message || req.body.description || '',
    button_text: req.body.button_text || 'Learn More',
    button_url: req.body.button_url || '/admission',
    start_date: req.body.start_date || '',
    end_date: req.body.end_date || '',
    image: { url: imageUrl },
    is_active: req.body.is_active !== 'false' && req.body.is_active !== false,
    display_order: schoolData.popups.length + 1
  };
  schoolData.popups.unshift(newPopup);
  res.redirect('/admin?tab=popups&msg=' + encodeURIComponent('Popup notice banner created!'));
});

app.post('/admin/popup/edit/:id', upload.single('image_file'), (req, res) => {
  if (!schoolData.popups) schoolData.popups = [];
  const id = parseInt(req.params.id);
  const popup = schoolData.popups.find(p => p.id === id);
  if (popup) {
    const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', popup.image ? popup.image.url : '/media/notices/admission_notice.png');
    popup.title = req.body.title || popup.title;
    popup.subtitle = req.body.subtitle !== undefined ? req.body.subtitle : popup.subtitle;
    popup.description = req.body.description !== undefined ? req.body.description : (req.body.message || popup.description);
    popup.message = req.body.message !== undefined ? req.body.message : (req.body.description || popup.message);
    popup.button_text = req.body.button_text !== undefined ? req.body.button_text : popup.button_text;
    popup.button_url = req.body.button_url !== undefined ? req.body.button_url : popup.button_url;
    popup.start_date = req.body.start_date !== undefined ? req.body.start_date : popup.start_date;
    popup.end_date = req.body.end_date !== undefined ? req.body.end_date : popup.end_date;
    popup.image = { url: imageUrl };
  }
  res.redirect('/admin?tab=popups&msg=' + encodeURIComponent('Popup banner updated!'));
});

app.post('/admin/popup/toggle/:id', (req, res) => {
  if (!schoolData.popups) schoolData.popups = [];
  const id = parseInt(req.params.id);
  const popup = schoolData.popups.find(p => p.id === id);
  if (popup) {
    popup.is_active = !popup.is_active;
  }
  res.redirect('/admin?tab=popups&msg=' + encodeURIComponent('Popup banner status toggled!'));
});

app.post('/admin/popup/delete/:id', (req, res) => {
  if (!schoolData.popups) schoolData.popups = [];
  const id = parseInt(req.params.id);
  schoolData.popups = schoolData.popups.filter(p => p.id !== id);
  res.redirect('/admin?tab=popups&msg=' + encodeURIComponent('Popup banner deleted!'));
});

// ADMIN POST ENDPOINTS - GALLERY (Add, Edit, Delete)
app.post('/admin/gallery/add', upload.single('image_file'), (req, res) => {
  const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', '/static/images/image/firstphoto.jpg');
  const catChoice = galleryCategoryChoices.find(c => c[0] === req.body.category);
  const newPhoto = {
    id: Date.now(),
    title: req.body.title || 'New Gallery Photo',
    category: req.body.category || 'school',
    get_category_display: catChoice ? catChoice[1] : req.body.category,
    image: { url: imageUrl },
    description: req.body.description || '',
    display_order: schoolData.gallery.length + 1,
    status: true
  };
  schoolData.gallery.unshift(newPhoto);
  res.redirect('/admin?tab=gallery&msg=' + encodeURIComponent('New gallery photo added successfully!'));
});

app.post('/admin/gallery/edit/:id', upload.single('image_file'), (req, res) => {
  const id = parseInt(req.params.id);
  const item = schoolData.gallery.find(g => g.id === id);
  if (item) {
    const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', item.image ? item.image.url : '/static/images/image/firstphoto.jpg');
    const catChoice = galleryCategoryChoices.find(c => c[0] === req.body.category);
    item.title = req.body.title || item.title;
    item.category = req.body.category || item.category;
    item.get_category_display = catChoice ? catChoice[1] : item.category;
    item.image = { url: imageUrl };
    item.description = req.body.description !== undefined ? req.body.description : item.description;
  }
  res.redirect('/admin?tab=gallery&msg=' + encodeURIComponent('Gallery photo updated!'));
});

app.post('/admin/gallery/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.gallery = schoolData.gallery.filter(g => g.id !== id);
  res.redirect('/admin?tab=gallery&msg=' + encodeURIComponent('Gallery photo deleted successfully!'));
});

// ADMIN POST ENDPOINTS - PROGRAMS (Add, Edit, Delete)
app.post('/admin/program/add', upload.single('image_file'), (req, res) => {
  const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', '/static/images/image/school gate.jpg');
  const newProg = {
    id: Date.now(),
    name: req.body.name,
    slug: slugify(req.body.name),
    duration: req.body.duration || '2 Years',
    eligibility: req.body.eligibility || 'Class 8 Passed',
    fee: 'Government Scale',
    description: req.body.description,
    image: { url: imageUrl },
    status: true
  };
  schoolData.programs.push(newProg);
  res.redirect('/admin?tab=programs&msg=' + encodeURIComponent('Academic program added successfully!'));
});

app.post('/admin/program/edit/:id', upload.single('image_file'), (req, res) => {
  const id = parseInt(req.params.id);
  const prog = schoolData.programs.find(p => p.id === id);
  if (prog) {
    const imageUrl = resolveImageUrl(req, 'image_file', 'image_url', prog.image ? prog.image.url : '/static/images/image/school gate.jpg');
    prog.name = req.body.name || prog.name;
    prog.slug = slugify(prog.name);
    prog.duration = req.body.duration || prog.duration;
    prog.eligibility = req.body.eligibility || prog.eligibility;
    prog.description = req.body.description || prog.description;
    prog.image = { url: imageUrl };
  }
  res.redirect('/admin?tab=programs&msg=' + encodeURIComponent('Academic program updated!'));
});

app.post('/admin/program/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.programs = schoolData.programs.filter(p => p.id !== id);
  res.redirect('/admin?tab=programs&msg=' + encodeURIComponent('Program deleted successfully!'));
});

// ADMIN POST ENDPOINTS - DOWNLOADS (Add, Delete)
app.post('/admin/download/add', (req, res) => {
  const newDownload = {
    title: req.body.title,
    category: req.body.category,
    file: { url: req.body.file_url || '/media/notices/pdf/calendar2083.pdf' },
    file_size: '500 KB',
    status: true
  };
  schoolData.downloads.push(newDownload);
  res.redirect('/admin?tab=downloads&msg=' + encodeURIComponent('Download resource added successfully!'));
});

app.post('/admin/download/delete/:title', (req, res) => {
  const title = decodeURIComponent(req.params.title);
  schoolData.downloads = schoolData.downloads.filter(d => d.title !== title);
  res.redirect('/admin?tab=downloads&msg=' + encodeURIComponent('Resource deleted successfully!'));
});

// ADMIN POST ENDPOINTS - ADMISSIONS & CONTACTS DELETE
app.post('/admin/admission/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.admissions = schoolData.admissions.filter(a => a.id !== id);
  res.redirect('/admin?tab=admissions&msg=' + encodeURIComponent('Admission application record deleted!'));
});

app.post('/admin/contact/delete/:id', (req, res) => {
  const id = parseInt(req.params.id);
  schoolData.contacts = schoolData.contacts.filter(c => c.id !== id);
  res.redirect('/admin?tab=contacts&msg=' + encodeURIComponent('Contact message deleted!'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${PORT}`);
});
