export function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-');
}

export const schoolData = {
  settings: {
    school_name: "Shree Jaljala Secondary School",
    tagline: "Quality Education for a Brighter Future from Nursery to Class 10 (SEE)",
    logo_url: "/static/images/logo.png",
    phone: "+977-9842000000 / +977-9800000000",
    email: "info@shreejaljala.edu.np",
    address: "Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Nepal",
    estd: "2045 B.S.",
    facebook_url: "https://facebook.com",
    youtube_url: "https://youtube.com"
  },
  sliders: [
    {
      id: 1,
      title: "Welcome to Shree Jaljala Secondary School",
      subtitle: "Empowering Students from Nursery to Class 10 with Excellence and Integrity",
      description: "Located in Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Shree Jaljala Secondary School is dedicated to nurturing holistic growth.",
      button_text: "Learn More",
      button_url: "/about",
      image: { url: "/static/images/slider1.jpg" },
      overlay_color: "#0b1b2b",
      overlay_opacity: 0.5,
      display_order: 1,
      status: true
    },
    {
      id: 2,
      title: "Quality Education in Sankhuwasabha",
      subtitle: "Providing Modern Science, Computer Literacy, and Balanced Learning",
      description: "Located in Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Shree Jaljala Secondary School is dedicated to nurturing holistic growth.",
      button_text: "Apply Now",
      button_url: "/admission",
      image: { url: "/static/images/slider2.jpg" },
      overlay_color: "#0b1b2b",
      overlay_opacity: 0.5,
      display_order: 2,
      status: true
    },
    {
      id: 3,
      title: "Holistic Physical & Cultural Development",
      subtitle: "Annual Sports Competitions, Saraswati Puja Celebrations & Creative Arts",
      description: "Located in Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Shree Jaljala Secondary School is dedicated to nurturing holistic growth.",
      button_text: "View Gallery",
      button_url: "/gallery",
      image: { url: "/static/images/slider3.jpg" },
      overlay_color: "#0b1b2b",
      overlay_opacity: 0.5,
      display_order: 3,
      status: true
    },
    {
      id: 4,
      title: "Dedicated & Inspiring Faculty",
      subtitle: "Qualified Teachers Nurturing Tomorrow's Citizens",
      description: "Located in Panchkhapan Municipality-7, Bihibare, Sankhuwasabha, Shree Jaljala Secondary School is dedicated to nurturing holistic growth.",
      button_text: "Meet Teachers",
      button_url: "/teachers",
      image: { url: "/static/images/slider4.jpg" },
      overlay_color: "#0b1b2b",
      overlay_opacity: 0.5,
      display_order: 4,
      status: true
    }
  ],

  teachers: [
    {
      id: 1,
      name: "Govinda Shrestha",
      slug: slugify("Govinda Shrestha"),
      photo: { url: "/media/teachers/govinda shrestha.jpg" },
      qualification: "M.Ed in Educational Management",
      department: "management",
      department_display: "School Management & Administration",
      position: "Principal",
      email: "govinda@jaljala.edu.np",
      phone: "9842011111",
      biography: "Dedicated educator leading Jaljala Secondary School towards academic excellence.",
      display_order: 1,
      status: true
    },
    {
      id: 2,
      name: "Bharat Bhattarai",
      slug: slugify("Bharat Bhattarai"),
      photo: { url: "/media/teachers/Bharat Bhattarai.jpg" },
      qualification: "M.Sc in Physics, B.Ed",
      department: "science",
      department_display: "Science & Mathematics",
      position: "Senior Science Teacher & Academic Coordinator",
      email: "bharat@jaljala.edu.np",
      phone: "9842022222",
      biography: "Over 15 years teaching Science & Mathematics for Class 9 and 10 SEE batches.",
      display_order: 2,
      status: true
    },
    {
      id: 3,
      name: "Bhubhan Pandey",
      slug: slugify("Bhubhan Pandey"),
      photo: { url: "/media/teachers/bhubhan pandey.jpg" },
      qualification: "M.A. in History, B.Ed",
      department: "social",
      department_display: "Social Studies & Arts",
      position: "Social Studies Department Head",
      email: "bhubhan@jaljala.edu.np",
      phone: "9842033333",
      biography: "Expert in Nepalese History, Geography and Civic Education.",
      display_order: 3,
      status: true
    },
    {
      id: 4,
      name: "Binita Limbu",
      slug: slugify("Binita Limbu"),
      photo: { url: "/media/teachers/binita limbu.jpg" },
      qualification: "M.A. in English Literature",
      department: "language",
      department_display: "Languages (Nepali & English)",
      position: "English Department Lead",
      email: "binita@jaljala.edu.np",
      phone: "9842044444",
      biography: "Passionate about English language fluency and communicative skills for basic & secondary levels.",
      display_order: 4,
      status: true
    },
    {
      id: 5,
      name: "Deepak Shrestha",
      slug: slugify("Deepak Shrestha"),
      photo: { url: "/media/teachers/deepak shrestha.jpg" },
      qualification: "B.Ed in Mathematics",
      department: "science",
      department_display: "Science & Mathematics",
      position: "Basic Level Incharge (Class 6-8)",
      email: "deepak@jaljala.edu.np",
      phone: "9842055555",
      biography: "Specializes in algebra, geometry, and foundational logic.",
      display_order: 5,
      status: true
    },
    {
      id: 6,
      name: "Dhanahang Rai",
      slug: slugify("Dhanahang Rai"),
      photo: { url: "/media/teachers/dhanahang rai.jpg" },
      qualification: "B.P.Ed (Physical Education)",
      department: "sports",
      department_display: "Sports & Physical Education",
      position: "Sports & Physical Education Instructor",
      email: "dhanahang@jaljala.edu.np",
      phone: "9842066666",
      biography: "Coordinates annual sports tournaments, football, volleyball, and physical fitness.",
      display_order: 6,
      status: true
    },
    {
      id: 7,
      name: "Dipa Pariyar",
      slug: slugify("Dipa Pariyar"),
      photo: { url: "/media/teachers/dipa pariyar.jpg" },
      qualification: "B.Ed in Primary Education",
      department: "primary",
      department_display: "Primary & Early Childhood",
      position: "Primary Level Teacher (Class 1-5)",
      email: "dipa@jaljala.edu.np",
      phone: "9842077777",
      biography: "Creating interactive, fun learning environments for primary students.",
      display_order: 7,
      status: true
    },
    {
      id: 8,
      name: "Indra Shrestha",
      slug: slugify("Indra Shrestha"),
      photo: { url: "/media/teachers/indra shrestha.jpg" },
      qualification: "B.Sc CSIT",
      department: "science",
      department_display: "Science & Mathematics",
      position: "Computer Science & IT Teacher",
      email: "indra@jaljala.edu.np",
      phone: "9842088888",
      biography: "Guides computer lab practicals, basic programming, and digital literacy.",
      display_order: 8,
      status: true
    },
    {
      id: 9,
      name: "Kamal Adhikari",
      slug: slugify("Kamal Adhikari"),
      photo: { url: "/media/teachers/kamal adhikari.jpg" },
      qualification: "B.B.S.",
      department: "management",
      department_display: "School Management & Administration",
      position: "Head of Administration & Accountant",
      email: "kamal@jaljala.edu.np",
      phone: "9842099999",
      biography: "Manages school records, finances, and official admissions.",
      display_order: 9,
      status: true
    },
    {
      id: 10,
      name: "Manoj Ghimire",
      slug: slugify("Manoj Ghimire"),
      photo: { url: "/media/teachers/manoj Ghimire.jpg" },
      qualification: "M.A. in Nepali Literature",
      department: "language",
      department_display: "Languages (Nepali & English)",
      position: "Senior Nepali Language Teacher",
      email: "manoj@jaljala.edu.np",
      phone: "9842100000",
      biography: "Promoting Nepali literature, grammar, and creative writing.",
      display_order: 10,
      status: true
    },
    {
      id: 11,
      name: "Pabitra Tamang",
      slug: slugify("Pabitra Tamang"),
      photo: { url: "/media/teachers/pabitra tamang.jpg" },
      qualification: "Montessori Trained",
      department: "primary",
      department_display: "Primary & Early Childhood",
      position: "Nursery & Kindergarten Lead",
      email: "pabitra@jaljala.edu.np",
      phone: "9842111111",
      biography: "Early childhood specialist guiding nursery & kindergarten toddlers.",
      display_order: 11,
      status: true
    },
    {
      id: 12,
      name: "Rajesh Basnet",
      slug: slugify("Rajesh Basnet"),
      photo: { url: "/media/teachers/rajesh basent.jpg" },
      qualification: "B.Sc in Chemistry",
      department: "science",
      department_display: "Science & Mathematics",
      position: "Science Lab Instructor",
      email: "rajesh@jaljala.edu.np",
      phone: "9842122222",
      biography: "Conducts practical physics and chemistry lab experiments for secondary students.",
      display_order: 12,
      status: true
    },
    {
      id: 13,
      name: "Shankar Basnet",
      slug: slugify("Shankar Basnet"),
      photo: { url: "/media/teachers/shankar basnet.jpg" },
      qualification: "M.Sc in Applied Mathematics",
      department: "science",
      department_display: "Science & Mathematics",
      position: "Optional Math & Science Teacher",
      email: "shankar@jaljala.edu.np",
      phone: "9842133333",
      biography: "Mentoring SEE students in Optional Mathematics.",
      display_order: 13,
      status: true
    },
    {
      id: 14,
      name: "Suga Rai",
      slug: slugify("Suga Rai"),
      photo: { url: "/media/teachers/suga rai.jpg" },
      qualification: "B.A. Fine Arts",
      department: "social",
      department_display: "Social Studies & Arts",
      position: "Arts & Cultural Activities Instructor",
      email: "suga@jaljala.edu.np",
      phone: "9842144444",
      biography: "Leads cultural dance, music, and festival celebrations.",
      display_order: 14,
      status: true
    },
    {
      id: 15,
      name: "Tara Vurtel",
      slug: slugify("Tara Vurtel"),
      photo: { url: "/media/teachers/tara vurtel.jpg" },
      qualification: "B.Ed in Primary Education",
      department: "primary",
      department_display: "Primary & Early Childhood",
      position: "Primary Education Teacher",
      email: "tara@jaljala.edu.np",
      phone: "9842155555",
      biography: "Fostering early childhood reading and numeracy.",
      display_order: 15,
      status: true
    }
  ],

  programs: [
    {
      id: 1,
      name: "Secondary Level (Class 9 - 10 / SEE Prep)",
      slug: slugify("Secondary Level Class 9 10 SEE Prep"),
      image: { url: "/static/images/image/image 14.jpg" },
      duration: "2 Years (Class 9 & 10)",
      eligibility: "Passed Class 8 Basic Level Examination",
      fee: "Government Subsidized / Free",
      description: "Comprehensive secondary education focusing on Science, Compulsory Mathematics, Optional Mathematics, English, Nepali, Social Studies, and Health/Population. Intensive SEE mock exams and science lab practicals.",
      display_order: 1,
      status: true
    },
    {
      id: 2,
      name: "Basic Level Education (Class 6 - 8)",
      slug: slugify("Basic Level Education Class 6 8"),
      image: { url: "/static/images/image/image 2.jpg" },
      duration: "3 Years (Class 6 to 8)",
      eligibility: "Passed Class 5 Primary Level",
      fee: "Free Education",
      description: "Foundational secondary preparation introducing Computer Science, General Science, Social Studies, and Vocational/Local Curriculum. Focus on problem solving, critical thinking, and character building.",
      display_order: 2,
      status: true
    },
    {
      id: 3,
      name: "Primary Level Education (Class 1 - 5)",
      slug: slugify("Primary Level Education Class 1 5"),
      image: { url: "/static/images/image/image 1.jpg" },
      duration: "5 Years (Class 1 to 5)",
      eligibility: "Age 5+ Years / Kindergarten Completion",
      fee: "Free Education",
      description: "Activity-based primary learning covering Nepali, English, Mathematics, Science, Social Studies, and Creative Arts. Features midday nutrition meals and interactive teaching methods.",
      display_order: 3,
      status: true
    },
    {
      id: 4,
      name: "Early Childhood & Pre-Primary (Nursery, LKG, UKG)",
      slug: slugify("Early Childhood Pre Primary Nursery LKG UKG"),
      image: { url: "/static/images/image/image 6.jpg" },
      duration: "3 Years (Nursery to UKG)",
      eligibility: "Age 3+ Years",
      fee: "Minimal Registration Fee",
      description: "Montessori-inspired play group and kindergarten education fostering child social skills, alphabet & number recognition, storytelling, and motor development in a safe environment.",
      display_order: 4,
      status: true
    },
    {
      id: 5,
      name: "Computer Literacy & Tech Lab Program",
      slug: slugify("Computer Literacy Tech Lab Program"),
      image: { url: "/static/images/image/image 4.jpg" },
      duration: "Integrated across Class 4 - 10",
      eligibility: "Enrolled Students of Jaljala School",
      fee: "Free Access",
      description: "Hands-on practical training in modern computer workstation lab, keyboard skills, MS Office suite, basic coding concepts, and safe internet research for academic assignments.",
      display_order: 5,
      status: true
    },
    {
      id: 6,
      name: "Sports & Physical Development Program",
      slug: slugify("Sports Physical Development Program"),
      image: { url: "/static/images/sport/sport 3.jpg" },
      duration: "Annual Co-Curricular",
      eligibility: "All Students (Class 1 - 10)",
      fee: "Included",
      description: "Structured physical education, athletics, football, volleyball, badminton tournaments, and traditional games promoting teamwork and sportsmanship.",
      display_order: 6,
      status: true
    }
  ],

  notices: [
    {
      id: 1,
      title: "Admission Open for Academic Year 2083 (Class Nursery to Class 9)",
      slug: slugify("Admission Open for Academic Year 2083 Class Nursery to Class 9"),
      description: "Application forms for new student admissions for Academic Session 2083 B.S. are now available online and at the school administration desk. Entrance test and document verification will be conducted from Shrawan 15.",
      category: "admission",
      category_display: "Admission Notice",
      featured: true,
      status: true,
      image: { url: "/static/images/image/schoolnotices.png" },
      created_at: new Date("2026-07-01")
    },
    {
      id: 2,
      title: "First Terminal Examination Schedule 2083",
      slug: slugify("First Terminal Examination Schedule 2083"),
      description: "Notice to all students and parents: First Terminal Examinations for Class 1 to 10 will commence from Shrawan 20 B.S. Students must collect their admit cards by Shrawan 18.",
      category: "exam",
      category_display: "Examination Notice",
      featured: true,
      status: true,
      image: { url: "/static/images/image/image 14.jpg" },
      created_at: new Date("2026-07-05")
    },
    {
      id: 3,
      title: "Merit & Need-Based Scholarship Form Deadline",
      slug: slugify("Merit Need Based Scholarship Form Deadline"),
      description: "Application deadline for government scholarships and municipal merit quotas is Shrawan 15. Eligible students from Ward No. 7 Panchkhapan are requested to submit certificates.",
      category: "academic",
      category_display: "Academic Notice",
      featured: false,
      status: true,
      image: { url: "/static/images/image/image 12.jpg" },
      created_at: new Date("2026-07-10")
    },
    {
      id: 4,
      title: "Annual Sports Week & Inter-House Tournament",
      slug: slugify("Annual Sports Week Inter House Tournament"),
      description: "Annual sports week competitions in Volleyball, Football, Relay Racing, and Chess will begin next month. Interested students should register with Dhanahang Rai (Sports Dept).",
      category: "event",
      category_display: "Event & Activity",
      featured: true,
      status: true,
      image: { url: "/static/images/sport/sport 4.jpg" },
      created_at: new Date("2026-07-15")
    }
  ],

  gallery: [
    // School Campus & Buildings
    { id: 1, title: "School Main Entrance Gate", category: "school", get_category_display: "School Campus & Buildings", image: { url: "/static/images/image/school gate.jpg" }, description: "Front view of Shree Jaljala Secondary School entrance in Panchkhapan-7, Bihibare.", display_order: 1, status: true },
    { id: 2, title: "School Building & Assembly Ground", category: "school", get_category_display: "School Campus & Buildings", image: { url: "/static/images/image/firstphoto.jpg" }, description: "Morning assembly and main academic wing.", display_order: 2, status: true },
    { id: 3, title: "Academic Complex Second View", category: "school", get_category_display: "School Campus & Buildings", image: { url: "/static/images/image/secondphoto.jpg" }, description: "View of secondary classroom blocks and playground.", display_order: 3, status: true },
    { id: 4, title: "Campus Courtyard & Greenery", category: "school", get_category_display: "School Campus & Buildings", image: { url: "/static/images/image/thirdphoto.jpg" }, description: "Peaceful environment surrounding the school campus.", display_order: 4, status: true },

    // Saraswati Puja & Cultural
    { id: 5, title: "Saraswati Puja Floral Rituals", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/media/gallery/saraswoti 1.jpg" }, description: "Students performing traditional Saraswati Puja rituals for knowledge and wisdom.", display_order: 5, status: true },
    { id: 6, title: "Saraswati Puja Worship & Prayers", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/static/images/saraswotipuja/saraswoti 2.jpg" }, description: "Devotional worship of Goddess Saraswati on Basanta Panchami.", display_order: 6, status: true },
    { id: 7, title: "Saraswati Puja Cultural Performance", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/media/gallery/saraswoti 3.jpg" }, description: "Cultural dance and musical offerings by secondary level students.", display_order: 7, status: true },
    { id: 8, title: "Music & Cultural Song Performance", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/static/images/saraswotipuja/saraswoti 4.jpg" }, description: "Traditional folk song and dance presentation by students.", display_order: 8, status: true },
    { id: 9, title: "Prasadam & Community Gathering", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/media/gallery/saraswoti 5.jpg" }, description: "Community gathering and prasadam distribution during festival.", display_order: 9, status: true },
    { id: 10, title: "Students Festival Group Celebration", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/static/images/saraswotipuja/saraswoti 6.jpg" }, description: "Class group photo during Saraswati Puja event.", display_order: 10, status: true },
    { id: 11, title: "Cultural Attire & Festival Moments", category: "cultural", get_category_display: "Cultural & Saraswati Puja", image: { url: "/static/images/saraswotipuja/saraswoti 7.jpg" }, description: "Students dressed in colorful Nepalese traditional attire.", display_order: 11, status: true },

    // Sports & Physical Education
    { id: 12, title: "Inter-House Volleyball Tournament", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/media/gallery/sport 2.jpg" }, description: "High-energy match between Red and Blue house volleyball teams.", display_order: 12, status: true },
    { id: 13, title: "Competitive Volleyball Smash Action", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/static/images/sport/sport 3.jpg" }, description: "Competitive volleyball match on the school sports court.", display_order: 13, status: true },
    { id: 14, title: "School Football Match & Ground", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/static/images/sport/sport 4.jpg" }, description: "Inter-class football tournament on school sports ground.", display_order: 14, status: true },
    { id: 15, title: "Athletics Sprint & Relay Races", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/static/images/sport/sport 5.jpg" }, description: "Students competing in 100m track sprint race.", display_order: 15, status: true },
    { id: 16, title: "High Jump & Field Competition", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/media/gallery/sport 6.jpg" }, description: "Annual sports day athletics event.", display_order: 16, status: true },
    { id: 17, title: "Inter-House Tug of War & Fun Sports", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/static/images/sport/sport 7.jpg" }, description: "Fun team competition during sports week.", display_order: 17, status: true },
    { id: 18, title: "School Sports Fitness Routine", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/media/gallery/sport 8.jpg" }, description: "Morning physical exercise and fitness drill.", display_order: 18, status: true },
    { id: 19, title: "Annual Sports Trophy & Award Ceremony", category: "sports", get_category_display: "Sports & Physical Education", image: { url: "/static/images/sport/sport 9.jpg" }, description: "Winners receiving medals and certificates from sports instructors.", display_order: 19, status: true },

    // Classroom Learning
    { id: 20, title: "Interactive Group Study Session", category: "classroom", get_category_display: "Classroom Learning", image: { url: "/static/images/image/sixphoto.jpg" }, description: "Students working collaboratively on project work.", display_order: 20, status: true },
    { id: 21, title: "Secondary Level Classroom Lecture", category: "classroom", get_category_display: "Classroom Learning", image: { url: "/static/images/image/image 13.jpg" }, description: "Engaging classroom instruction in SEE preparation class.", display_order: 21, status: true },
    { id: 22, title: "Primary Level Interactive Learning", category: "classroom", get_category_display: "Classroom Learning", image: { url: "/static/images/image/image 1.jpg" }, description: "Activity-based learning for young learners.", display_order: 22, status: true },

    // Science & Computer Labs
    { id: 23, title: "Science Lab Biology Microscope Practical", category: "laboratory", get_category_display: "Science & Computer Labs", image: { url: "/static/images/image/fourthphoto.jpg" }, description: "Students observing microscope slide specimens in biology lab.", display_order: 23, status: true },
    { id: 24, title: "Computer Lab Practical Workstation", category: "laboratory", get_category_display: "Science & Computer Labs", image: { url: "/static/images/image/image 4.jpg" }, description: "Students practicing digital literacy and typing in computer lab.", display_order: 24, status: true },

    // Events & Official Visits
    { id: 25, title: "Mayor Inspection & Official Visit", category: "events", get_category_display: "Events & Official Visits", image: { url: "/static/images/image/mayor.jpg" }, description: "Mayor of Panchkhapan Municipality inspecting school infrastructure.", display_order: 25, status: true },
    { id: 26, title: "School Management Committee Meeting", category: "events", get_category_display: "Events & Official Visits", image: { url: "/static/images/photos/head management.jpg" }, description: "School administration and management committee conference.", display_order: 26, status: true },
    { id: 27, title: "Honor to Former Principal & Leaders", category: "events", get_category_display: "Events & Official Visits", image: { url: "/static/images/photos/formerprinciple.jpg" }, description: "Felicitation program honoring veteran educators and former principal.", display_order: 27, status: true },
    { id: 28, title: "Annual Parents & Teachers Assembly", category: "events", get_category_display: "Events & Official Visits", image: { url: "/static/images/image/image 12.jpg" }, description: "Parents-teachers interaction program discussing student progress.", display_order: 28, status: true },

    // Educational Tours
    { id: 29, title: "Educational Field Excursion", category: "tour", get_category_display: "Educational Tours", image: { url: "/static/images/image/fifthphoto.jpg" }, description: "Students on educational field visit to local hydropower station.", display_order: 29, status: true },
    { id: 30, title: "Botanical & Nature Study Excursion", category: "tour", get_category_display: "Educational Tours", image: { url: "/static/images/image/sevenphoto.jpg" }, description: "Science students exploring regional flora and environmental geography.", display_order: 30, status: true },
    { id: 31, title: "Cultural Heritage Study Tour", category: "tour", get_category_display: "Educational Tours", image: { url: "/static/images/image/eightphoto.jpg" }, description: "Educational tour visiting historical sites in Sankhuwasabha.", display_order: 31, status: true }
  ],

  testimonials: [
    {
      name: "Ramesh Thapa",
      role: "Parent of Class 9 Student",
      quote: "Jaljala Secondary School has provided an outstanding environment for my son. The science labs, sports, and disciplined teaching have boosted his confidence tremendously.",
      rating: 5
    },
    {
      name: "Sunita Rai",
      role: "SEE Graduate (Batch 2079 B.S.)",
      quote: "Studying at Jaljala School laid a solid foundation for my higher education. The teachers are helpful, patient, and dedicated to every student's success.",
      rating: 5
    }
  ],

  downloads: [
    {
      title: "Academic Calendar & Holiday List 2083 B.S.",
      category: "routine",
      file: { url: "/media/notices/pdf/calendar2083.pdf" },
      file_size: "450 KB",
      status: true
    },
    {
      title: "Class 10 (SEE) Model Question Sets & Syllabus",
      category: "syllabus",
      file: { url: "/media/notices/pdf/see_syllabus.pdf" },
      file_size: "1.8 MB",
      status: true
    },
    {
      title: "School Admission Application Form (Printable)",
      category: "form",
      file: { url: "/media/notices/pdf/admission_form.pdf" },
      file_size: "280 KB",
      status: true
    }
  ],

  popups: [
    {
      id: 1,
      title: "Admission Open for Academic Session 2083",
      subtitle: "Shree Jaljala Secondary School, Panchkhapan-7, Sankhuwasabha",
      image: { url: "/media/notices/admission_notice.png" },
      message: "Online admission applications are now open for Nursery to Class 9 (SEE Level). Submit your application online or visit the school administration office.",
      button_text: "Fill Online Admission Form",
      button_url: "/admission",
      is_active: true
    }
  ],

  admissions: [],
  contacts: []
};

export const departmentChoices = [
  ['management', 'School Management & Administration'],
  ['science', 'Science & Mathematics'],
  ['language', 'Languages (Nepali & English)'],
  ['social', 'Social Studies & Arts'],
  ['primary', 'Primary & Early Childhood'],
  ['sports', 'Sports & Physical Education'],
];

export const noticeCategoryChoices = [
  ['admission', 'Admission Notice'],
  ['exam', 'Examination Notice'],
  ['academic', 'Academic Notice'],
  ['event', 'Event & Activity'],
  ['general', 'General Announcement'],
];

export const galleryCategoryChoices = [
  ['school', 'School Campus & Buildings'],
  ['cultural', 'Cultural & Saraswati Puja'],
  ['sports', 'Sports & Physical Education'],
  ['classroom', 'Classroom Learning'],
  ['laboratory', 'Science & Computer Labs'],
  ['events', 'Events & Official Visits'],
  ['tour', 'Educational Tours'],
];
