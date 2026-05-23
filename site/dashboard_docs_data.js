(function () {
    var groupedGroupDocs = {
        Acct_Fin_Ops: {
            baseId: "group-accounting-finance-ops",
            title: "Accounting/Finance/Ops",
            tag: "Small Group",
            rule: "Groups accounting, finance, business analytics, real-estate, and operations/supply-chain majors that map into a shared business-quant bucket.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Accounting",
                "Bus Adm - Real Estate Studies",
                "Bus Admin - Accounting",
                "Bus Admin - Business Analytics",
                "Bus Admin - Financial Mgmt",
                "Bus Admin - Op&Supl Chain Mgmt",
                "Financial Management",
                "Operations & Supply Chain Mgmt"
            ]
        },
        Mgmt: {
            baseId: "group-management",
            title: "Management",
            tag: "Small Group",
            rule: "Groups broad management and leadership majors that prepare students for general business administration and people-management pathways.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Bus Admin - Gen Business Mgmt",
                "Bus Admin - Human Resc Mgmt",
                "Bus Admin - Leadership& Mgmt",
                "Business Administration",
                "Human Resources Management",
                "Leadership & Management"
            ]
        },
        OtherBusiness: {
            baseId: "group-specialized-business",
            title: "Specialized Business",
            tag: "Small Group",
            rule: "Groups smaller business subfields such as law/compliance, entrepreneurship, international business, and business communication.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Bus Adm - Law & Compliance",
                "Bus Admin - Communication",
                "Bus Admin - Entrepreneurship",
                "Bus Admin - Intl Business",
                "Business Communication",
                "Entrepreneurship",
                "International Business",
                "Law & Compliance"
            ]
        },
        Mktg: {
            baseId: "group-marketing",
            title: "Marketing",
            tag: "Small Group",
            rule: "Keeps marketing as its own grouped-major bucket because it behaves distinctly from broader management and communication buckets.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Bus Admin - Marketing Mgmt",
                "Marketing Management"
            ]
        },
        Writing_Comm: {
            baseId: "group-writing-communication",
            title: "Writing/Communication",
            tag: "Small Group",
            rule: "Groups communication, journalism, digital media, and English writing programs that emphasize media, messaging, and content.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Communication Studies",
                "Digital Media Arts",
                "English",
                "English - Creative Writing",
                "Journalism",
                "Strategic Comm: Ad and PR"
            ]
        },
        Humanities: {
            baseId: "group-humanities",
            title: "Humanities",
            tag: "Small Group",
            rule: "Groups humanities, arts, music, history, philosophy, and theology majors that share a broad liberal-arts orientation.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Art History",
                "Catholic Studies",
                "Film Studies",
                "History",
                "Music",
                "Music - Business",
                "Music - Performance",
                "Philosophy",
                "Theology",
                "Women/Gender/Sexuality Studies"
            ]
        },
        Social: {
            baseId: "group-social-sciences",
            title: "Social Sciences",
            tag: "Small Group",
            rule: "Groups social-science and public-affairs majors such as economics variants, political science, psychology, sociology, and related interdisciplinary programs.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Criminal Justice",
                "Economics",
                "Economics - Business",
                "Economics - Mathematical",
                "Economics - Public Policy",
                "Environmental Studies",
                "Family Studies",
                "Geography - Geo Info Sys (GIS)",
                "International Studies",
                "Intl Studies - Pol Sci",
                "Political Science",
                "Psychology",
                "Sociology"
            ]
        },
        Other: {
            baseId: "group-pre-professional-undeclared",
            title: "Pre-Professional/Undeclared",
            tag: "Small Group",
            rule: "Groups undecided and pre-professional incoming pathways that do not land in a mirrored graduating grouped-major bucket.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Education-Elementary Education",
                "Education-Secondary Education",
                "Pre-Dentistry",
                "Pre-Law",
                "Pre-Medicine",
                "Pre-Physical Therapy",
                "Pre-Physician Assistant",
                "Undecided"
            ]
        },
        EDUC: {
            baseId: "group-education",
            title: "Education",
            tag: "Small Group",
            rule: "Groups teacher-preparation and school-based education majors into one dedicated education bucket.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Comm. Arts & Lit (5-12)",
                "Elementary Education (K-6)",
                "Instrumental Music (K-12)",
                "K-12 Music Education",
                "Middle/Secondary Education",
                "Soc Studies (5-12) - History",
                "Soc Studies (5-12) - Pol. Sci.",
                "Vocal Music (K-12)"
            ]
        },
        COH: {
            baseId: "group-health-sciences",
            title: "Health Sciences",
            tag: "Small Group",
            rule: "Groups health and wellness majors, including nursing and social work, into one health-facing bucket.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Exercise Science",
                "Health Promotion & Wellness",
                "Nursing",
                "Public Health",
                "Social Work"
            ]
        },
        Science: {
            baseId: "group-natural-sciences",
            title: "Natural Sciences",
            tag: "Small Group",
            rule: "Groups natural-science majors such as biology, chemistry, neuroscience, geology, and physics.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Biochemistry",
                "Biology",
                "Biology (BS)",
                "Biology of Global Health",
                "Chemistry",
                "Chemistry (ACS Certified)",
                "Environmental Science",
                "Geology",
                "Neuroscience",
                "Physics"
            ]
        },
        Engineering: {
            baseId: "group-engineering",
            title: "Engineering",
            tag: "Small Group",
            rule: "Groups engineering disciplines together because they form a coherent and high-volume technical pathway.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Civil Engineering",
                "Computer Engineering",
                "Electrical Engineering",
                "Mechanical Engineering"
            ]
        },
        CS_DS_DA_Math_Stat: {
            baseId: "group-computing-data-math-stats",
            title: "Computing/Data/Math/Stats",
            tag: "Small Group",
            rule: "Groups computing, data, mathematics, and statistics majors that share quantitative and technical preparation.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "Actuarial Science",
                "Comp Science BS (Master Track)",
                "Computer Science (BS)",
                "Data Analytics",
                "Data Science",
                "Mathematics",
                "Mathematics (B.S.)",
                "Mathematics (Education Track)",
                "Statistics"
            ]
        },
        Lang: {
            baseId: "group-languages",
            title: "Languages",
            tag: "Small Group",
            rule: "Groups language majors that appear only on the graduating side of the current grouped dataset.",
            listTitle: "Actual majors in this grouped bucket",
            majors: [
                "German",
                "German (IEP)",
                "Spanish Cultural/Literary St.",
                "Spanish Linguistics/Lang. St."
            ]
        }
    };

    window.DASHBOARD_DOCS_DATA = {
        career: {
            methodologyIntro: "These notes live directly on the dashboard so the clustering logic, weighting assumptions, and caveats stay visible while you read the chart.",
            methodology: [
                {
                    id: "how-to-read",
                    title: "How to read this chart",
                    tag: "Guide",
                    note: "Ribbon width shows how many classified graduates move from a major cluster to a career field.",
                    rule: "Each outside arc is a cluster, each ribbon is a non-zero connection, and the ribbon color follows the major family rather than the career field.",
                    paragraphs: [
                        "The left-side major clusters are grouped into four larger academic families, while the right-side destinations are grouped into eight job-function fields.",
                        "Hovering or clicking a tile keeps the same exact-focus image behavior that was already on the page."
                    ],
                    open: true
                },
                {
                    id: "weighting-rule",
                    title: "Weighting rule",
                    tag: "Method",
                    note: "Each classified graduate contributes one unit to one major cluster and one unit to one career field.",
                    rule: "This dashboard is not using the two-unit grouped-major weighting used by the incoming-to-graduating pages; ribbon widths here represent counted classified graduates.",
                    paragraphs: [
                        "That is why the page total stays at 2682 graduates rather than doubling to a weighted-unit total."
                    ]
                },
                {
                    id: "connection-rule",
                    title: "Connection rule",
                    tag: "Rule",
                    note: "A ribbon appears only when at least one classified graduate falls into that major-to-career combination.",
                    rule: "No extra smoothing or synthetic links are added beyond the classified records in the filtered lookup that drives this render.",
                    paragraphs: [
                        "The chart therefore emphasizes where graduates actually land in the clustered dataset rather than every possible conceptual pathway."
                    ]
                },
                {
                    id: "classification-rules",
                    title: "Grouping / classification rule",
                    tag: "Rule",
                    note: "Major clusters come from the current merged taxonomy and career fields are based on job function, not employer industry.",
                    rule: "A software engineer at a bank stays in Software & Data, and an accountant at a hospital stays in Finance & Accounting, because the role function matters more than the employer label.",
                    paragraphs: [
                        "Small major clusters were merged only where the page needed broader, readable buckets; Economics, Engineering, and Computer Science & IT were intentionally kept visible as distinct clusters."
                    ]
                },
                {
                    id: "limits-caveats",
                    title: "Limits / caveats",
                    tag: "Limits",
                    note: "This view trades some program-level detail for a cleaner read of the major-to-career structure.",
                    rule: "Merged clusters simplify dozens of majors into 13 small major buckets and eight career fields, so fine-grained distinctions are intentionally compressed.",
                    paragraphs: [
                        "Only classified records in the current filtered lookup appear here, and ambiguous job titles were assigned to the most defensible functional bucket available."
                    ]
                }
            ],
            sections: {
                business: {
                    id: "family-business-management",
                    title: "Business & Management",
                    tag: "Large Group",
                    rule: "This family groups majors centered on finance, business administration, operations, analytics, and specialized organizational functions.",
                    groupKeys: [
                        "major_Finance_Accounting",
                        "major_General_Business",
                        "major_Operations_Analytics",
                        "major_Specialized_Business"
                    ]
                },
                humanities: {
                    id: "family-humanities-communication",
                    title: "Humanities & Communication",
                    tag: "Large Group",
                    rule: "This family groups language, arts, writing, media, marketing, and communication programs that share expression- and audience-facing pathways.",
                    groupKeys: [
                        "major_Languages_Arts_Humanities",
                        "major_Marketing_Communication"
                    ]
                },
                social: {
                    id: "family-social-sciences-education",
                    title: "Social Sciences & Education",
                    tag: "Large Group",
                    rule: "This family groups education, public-affairs, social-science, and service-oriented programs, while still preserving Economics as its own small cluster.",
                    groupKeys: [
                        "major_Economics",
                        "major_Social_Sciences_Humanities",
                        "major_Education_Social_Services"
                    ]
                },
                stem: {
                    id: "family-engineering-science-technology",
                    title: "Engineering, Science & Technology",
                    tag: "Large Group",
                    rule: "This family groups technical and science majors while keeping engineering, computing, life sciences, and physical sciences separate where their outcomes meaningfully differ.",
                    groupKeys: [
                        "major_Physical_Environmental_Sciences",
                        "major_Biological_Health_Sciences",
                        "major_Computer_Science_IT",
                        "major_Engineering"
                    ]
                },
                careers: {
                    id: "career-clusters",
                    title: "Career Fields (8)",
                    tag: "Career Overview",
                    rule: "These right-side clusters are based on job function rather than employer industry, so the field reflects the work graduates do, not just where they work.",
                    listTitle: "Career fields on this page",
                    list: [
                        "Finance & Accounting",
                        "Management & Ops",
                        "Sales & Marketing",
                        "Legal & Policy",
                        "Education & Social Service",
                        "Health & Science Research",
                        "Software & Data",
                        "Engineering"
                    ],
                    groupKeys: [
                        "career_Finance_Accounting",
                        "career_Management_Ops",
                        "career_Sales_Marketing",
                        "career_Legal_Policy",
                        "career_Education_Social_Service",
                        "career_Health_Science_Research",
                        "career_Software_Data",
                        "career_Engineering"
                    ]
                }
            },
            items: {
                major_Finance_Accounting: {
                    id: "major-finance-accounting",
                    title: "Finance & Accounting",
                    tag: "Small Group",
                    rule: "Groups accounting, finance, actuarial, and insurance-focused business programs that point toward financial analysis, audit, and investment work.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Accounting",
                        "Actuarial Science",
                        "Financial Management",
                        "Risk Management and Insurance"
                    ]
                },
                major_General_Business: {
                    id: "major-general-business",
                    title: "General Business",
                    tag: "Small Group",
                    rule: "Holds broad business administration and MBA-style programs that are not specialized enough to sit only in finance, operations, or a niche business bucket.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Business Administration",
                        "Entrepreneurship",
                        "Executive MBA",
                        "Health Care MBA",
                        "Part-Time Flex MBA"
                    ]
                },
                major_Operations_Analytics: {
                    id: "major-operations-analytics",
                    title: "Operations & Analytics",
                    tag: "Small Group",
                    rule: "Captures business analytics, supply chain, operations, and technology-management programs with a process or decision-support focus.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Data Analytics",
                        "MS Business Analytics",
                        "Operations & Supply Chain Mgmt",
                        "Technology Management"
                    ]
                },
                major_Specialized_Business: {
                    id: "major-specialized-business",
                    title: "Specialized Business",
                    tag: "Small Group",
                    rule: "Bundles smaller business subfields such as HR, compliance, org change, international business, real estate, and related leadership tracks.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Human Resources Management",
                        "International Business",
                        "Law & Compliance",
                        "Org. Ethics & Compliance",
                        "Organization Develop & Change",
                        "Publc Safety & Law Enfr Ldrshp",
                        "Real Estate Studies",
                        "U.S. Law"
                    ]
                },
                major_Languages_Arts_Humanities: {
                    id: "major-languages-arts-humanities",
                    title: "Languages, Arts & Humanities",
                    tag: "Small Group",
                    rule: "Combines languages, arts, music, theology, and writing-heavy humanities programs that are better read together than as tiny standalone slices.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Art History",
                        "Catholic Studies",
                        "English",
                        "English - Professional Writing",
                        "French",
                        "Music",
                        "Music - Business",
                        "Music - Performance",
                        "Pastoral Leadership",
                        "Pastoral Ministry",
                        "Spanish",
                        "Spanish Cultural/Literary St.",
                        "Spanish Linguistics/Lang. St.",
                        "Theology"
                    ]
                },
                major_Marketing_Communication: {
                    id: "major-marketing-communication",
                    title: "Marketing & Communication",
                    tag: "Small Group",
                    rule: "Brings together marketing, communication, journalism, media, and creative-writing programs because they share audience, messaging, and content-oriented pathways.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Business Communication",
                        "COJO Creative Multimedia",
                        "COJO Interpersonal Comm",
                        "COJO Journalism",
                        "COJO Persuasion/Soc Influence",
                        "COJO Strategic Communications",
                        "Communication Studies",
                        "Communication and Journalism",
                        "Creative Writing & Publishing",
                        "Digital Media Arts",
                        "English - Creative Writing",
                        "Journalism",
                        "Marketing Management",
                        "Strategic Comm: Ad and PR",
                        "Strategic Communication"
                    ]
                },
                major_Economics: {
                    id: "major-economics",
                    title: "Economics",
                    tag: "Small Group",
                    rule: "Keeps economics separate so its outcome pattern stays visible instead of being absorbed into broader business or social-science buckets.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Economics",
                        "Economics - Business",
                        "Economics - International",
                        "Economics - Mathematical",
                        "Economics - Public Policy"
                    ]
                },
                major_Social_Sciences_Humanities: {
                    id: "major-social-sciences-humanities",
                    title: "Social Sciences & Humanities",
                    tag: "Small Group",
                    rule: "Groups public-affairs, behavior, justice, liberal-arts, and interdisciplinary social-science programs with similar people-, policy-, and society-oriented pathways.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Counseling Psychology",
                        "Criminal Justice",
                        "History",
                        "Intl Studies - Economics",
                        "Intl Studies - History",
                        "Intl Studies - Pol Sci",
                        "Justice & Peace Studies",
                        "Liberal Arts",
                        "Philosophy",
                        "Political Science",
                        "Psychology",
                        "Sociology"
                    ]
                },
                major_Education_Social_Services: {
                    id: "major-education-social-services",
                    title: "Education & Social Services",
                    tag: "Small Group",
                    rule: "Combines teaching, student-support, educational leadership, and social-work programs into one applied education-and-service cluster.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Acad Behavioral Strategist",
                        "Autism Spectrum Disorders",
                        "Early Childhood Special Educ",
                        "Educ Leadership & Learning",
                        "Educational Leadership & Admin",
                        "Educational Studies",
                        "Elementary Education (K-6)",
                        "K-12 Music Education",
                        "K-12 World Lang. & Cultures",
                        "Leadership In Student Affairs",
                        "Middle/Secondary Education",
                        "Music Education",
                        "Social Work",
                        "Teacher Preparation - K-12",
                        "Teacher Preparation-Elem K-6",
                        "Teacher Preparation-Secondary"
                    ]
                },
                major_Physical_Environmental_Sciences: {
                    id: "major-physical-environmental-sciences",
                    title: "Physical & Environmental Sciences",
                    tag: "Small Group",
                    rule: "Groups physical science, earth science, geography, and environmental science programs that would otherwise be too small and fragmented on their own.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Chemistry",
                        "Environmental Science",
                        "Environmental Studies",
                        "Geography",
                        "Geography - Geo Info Sys (GIS)",
                        "Geology",
                        "Geology (BS)",
                        "Physics",
                        "Regulatory Science"
                    ]
                },
                major_Biological_Health_Sciences: {
                    id: "major-biological-health-sciences",
                    title: "Biological & Health Sciences",
                    tag: "Small Group",
                    rule: "Combines life-science, public-health, nursing, neuroscience, and wellness programs into one health- and bioscience-facing cluster.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Biochemistry",
                        "Biology",
                        "Biology (BS)",
                        "Biology of Global Health",
                        "Environmental Sci (Biology)",
                        "Exercise Science",
                        "Health Promotion & Wellness",
                        "MS Health Care Innovation",
                        "Neuroscience",
                        "Nursing",
                        "Public Health"
                    ]
                },
                major_Computer_Science_IT: {
                    id: "major-computer-science-it",
                    title: "Computer Science & IT",
                    tag: "Small Group",
                    rule: "Keeps computing, software, IT, and data-intensive technical programs together while remaining separate from engineering.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Computer Science",
                        "Computer Science (BS)",
                        "Data Science",
                        "Information Technology",
                        "Quant Methods - Computer Sci",
                        "Software Engineering",
                        "Software Management"
                    ]
                },
                major_Engineering: {
                    id: "major-engineering",
                    title: "Engineering",
                    tag: "Small Group",
                    rule: "Keeps engineering disciplines distinct from computing and lab sciences because they feed different functional career pathways.",
                    listTitle: "Actual majors in this cluster",
                    list: [
                        "Civil Engineering",
                        "Computer Engineering",
                        "Electrical Engineering",
                        "Manufacturing Engineering",
                        "Mechanical Engineering",
                        "Systems Engineering"
                    ]
                },
                career_Finance_Accounting: {
                    id: "career-finance-accounting",
                    title: "Finance & Accounting",
                    tag: "Career Field",
                    rule: "Includes accounting, audit, actuarial, investment, corporate-finance, and closely related financial-analysis functions.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Financial Analyst",
                        "Actuarial Analyst",
                        "Audit Associate",
                        "Accountant",
                        "Tax Associate",
                        "Investment Analyst",
                        "Financial Advisor",
                        "Staff Accountant"
                    ]
                },
                career_Management_Ops: {
                    id: "career-management-ops",
                    title: "Management & Ops",
                    tag: "Career Field",
                    rule: "Includes general management, operations, project/program coordination, consulting, recruiting, and other business-execution roles.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Associate",
                        "Marketing Coordinator",
                        "Project Manager",
                        "Business Analyst",
                        "Account Manager",
                        "Program Manager",
                        "Inventory Analyst",
                        "Associate Consultant"
                    ]
                },
                career_Sales_Marketing: {
                    id: "career-sales-marketing",
                    title: "Sales & Marketing",
                    tag: "Career Field",
                    rule: "Includes sales, brand, growth, client-development, account-executive, and marketing execution roles.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Sales Development Representative",
                        "Marketing Specialist",
                        "Sales Associate",
                        "Business Development Representative",
                        "Marketing Associate",
                        "Sales Representative",
                        "Digital Marketing Specialist",
                        "Account Executive"
                    ]
                },
                career_Legal_Policy: {
                    id: "career-legal-policy",
                    title: "Legal & Policy",
                    tag: "Career Field",
                    rule: "Includes law, compliance, policy, public-safety, regulatory, and adjacent governance-oriented roles.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Paralegal",
                        "Compliance Services Associate",
                        "Police Sergeant",
                        "Compliance Manager",
                        "Public Policy Intern",
                        "Legal Assistant and Intake Specialist",
                        "Compliance Director",
                        "Intelligence Officer"
                    ]
                },
                career_Education_Social_Service: {
                    id: "career-education-social-service",
                    title: "Education & Social Service",
                    tag: "Career Field",
                    rule: "Includes classroom teaching, school support, advising, casework, social-service, and related community-support roles.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Teacher",
                        "Special Education Teacher",
                        "Social Worker",
                        "Case Manager",
                        "Clinical Social Worker",
                        "3rd Grade Teacher",
                        "Child Support Officer",
                        "Assistant Professor"
                    ]
                },
                career_Health_Science_Research: {
                    id: "career-health-science-research",
                    title: "Health & Science Research",
                    tag: "Career Field",
                    rule: "Includes clinical support, therapy, laboratory, research, and broader health-science roles that were merged into one readable destination field.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Medical Scribe",
                        "Mental Health Practitioner",
                        "Resident Assistant",
                        "Intern",
                        "Pre-Licensed Therapist",
                        "Scribe",
                        "Outpatient Therapist",
                        "Research Associate"
                    ]
                },
                career_Software_Data: {
                    id: "career-software-data",
                    title: "Software & Data",
                    tag: "Career Field",
                    rule: "Includes software engineering, IT/infrastructure, data, systems, and technical analytics roles under one computing field.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Software Engineer",
                        "Analyst",
                        "Data Analyst",
                        "Data Engineer",
                        "Data Scientist",
                        "Software Developer",
                        "Software Engineering Associate",
                        "Systems Analyst"
                    ]
                },
                career_Engineering: {
                    id: "career-engineering",
                    title: "Engineering",
                    tag: "Career Field",
                    rule: "Includes design, manufacturing, hardware, process, and traditional engineering roles kept separate from software/data work.",
                    listTitle: "Representative job titles in this field",
                    list: [
                        "Mechanical Engineer",
                        "Project Engineer",
                        "Manufacturing Engineer",
                        "Design Engineer",
                        "Mechanical Design Engineer",
                        "Electrical Engineer",
                        "Quality Engineer",
                        "Automation Engineer"
                    ]
                }
            }
        },
        grouped: {
            methodologyIntro: "These notes stay on the grouped-major dashboard so the weighting, transition rules, and grouped-major definitions are visible without leaving the chart.",
            methodology: [
                {
                    id: "grouped-how-to-read",
                    title: "How to read this chart",
                    tag: "Guide",
                    note: "The left side shows incoming grouped majors and the right side shows graduating grouped majors.",
                    rule: "Each ribbon is a non-zero transition between grouped-major buckets, and the ribbon color follows the grouped-major family on the page.",
                    paragraphs: [
                        "This view is a readability layer over the underlying major-level data, so it emphasizes broad movement patterns rather than every program-level distinction.",
                        "Hovering or clicking still drives the same exact-focus images already built into the dashboard."
                    ],
                    open: true
                },
                {
                    id: "grouped-weighting-rule",
                    title: "Weighting rule",
                    tag: "Method",
                    note: "Each student contributes two total ribbon units in this grouped-major view.",
                    rule: "A single-major student contributes both units to one graduating target, while a double-major student splits one unit to each of two graduating targets.",
                    paragraphs: [
                        "That is why the ring totals add to 1850 weighted units on each side even though the underlying student count is 925."
                    ]
                },
                {
                    id: "grouped-connection-rule",
                    title: "Connection rule",
                    tag: "Rule",
                    note: "A ribbon appears only when the grouped dataset contains at least one non-zero transition for that pair.",
                    rule: "This page does not add invented links between grouped majors; it only shows the transitions that exist in the current grouped-major structure."
                },
                {
                    id: "grouped-grouping-rule",
                    title: "Grouping / classification rule",
                    tag: "Rule",
                    note: "Grouped-major labels come from the current major.csv grouping map, with display names cleaned for readability.",
                    rule: "Programs were merged into grouped buckets when the dashboard needed broader, more interpretable slices than the raw major list would provide.",
                    paragraphs: [
                        "Pre-Professional/Undeclared appears only on the incoming side of the current data, and Languages appears only on the graduating side."
                    ]
                },
                {
                    id: "grouped-limits-caveats",
                    title: "Limits / caveats",
                    tag: "Limits",
                    note: "This grouped view intentionally compresses distinct majors into readable buckets.",
                    rule: "The page is best for understanding broad transition structure, not for making program-level claims about tiny major differences.",
                    paragraphs: [
                        "Some majors that are separate elsewhere in the project share a bucket here so the incoming-to-graduating story stays readable."
                    ]
                }
            ],
            families: {
                business: {
                    baseId: "family-business-management",
                    title: "Business & Management",
                    tag: "Large Group",
                    rule: "This family groups business-oriented buckets for finance, management, and smaller applied business pathways."
                },
                humanities: {
                    baseId: "family-humanities-communication",
                    title: "Humanities & Communication",
                    tag: "Large Group",
                    rule: "This family groups marketing, communication, writing, humanities, and language buckets that are primarily message- and culture-oriented."
                },
                social: {
                    baseId: "family-social-sciences-education",
                    title: "Social Sciences & Education",
                    tag: "Large Group",
                    rule: "This family groups social-science, education, and undeclared/pre-professional pathways to show broader student movement across people- and service-oriented programs."
                },
                stem: {
                    baseId: "family-engineering-science-health",
                    title: "Engineering, Science & Health",
                    tag: "Large Group",
                    rule: "This family groups engineering, computing/data, natural science, and health-science buckets while keeping those themes distinct as small groups."
                }
            },
            groups: groupedGroupDocs
        },
        groupedCollege: {
            methodologyIntro: "These notes stay on the college-color dashboard so the recoloring logic, weighting rules, and grouped-major definitions are visible next to the chart.",
            methodology: [
                {
                    id: "college-how-to-read",
                    title: "How to read this chart",
                    tag: "Guide",
                    note: "This page keeps the same grouped-major transitions as the original grouped dashboard but recolors and reorders them by college.",
                    rule: "Grouped-major labels still represent the same underlying buckets; only the visual organization rule changes on this page.",
                    paragraphs: [
                        "Any grouped-major tile inside a college block previews the full college-level block for that side, because the exact-focus images here are built at the college-block level.",
                        "Hovering or clicking still uses the same focus behavior that was already on the page."
                    ],
                    open: true
                },
                {
                    id: "college-weighting-rule",
                    title: "Weighting rule",
                    tag: "Method",
                    note: "This page uses the same two-unit grouped-major weighting as the original grouped dashboard.",
                    rule: "A single-major student contributes two units to one graduating target, while a double-major student splits one unit to each of two graduating targets.",
                    paragraphs: [
                        "The recoloring and reordering did not create a new weighted dataset; they only changed how the existing grouped-major structure is displayed."
                    ]
                },
                {
                    id: "college-connection-rule",
                    title: "Connection rule",
                    tag: "Rule",
                    note: "Ribbons still represent the same non-zero grouped-major transitions used on the original grouped page.",
                    rule: "This page does not change which transitions exist; it only recolors them by college and clusters same-college groups together around the circle."
                },
                {
                    id: "college-grouping-rule",
                    title: "Grouping / classification rule",
                    tag: "Rule",
                    note: "Grouped-major labels stay fixed, but the visual family assignment follows college rather than the original grouped-major theme families.",
                    rule: "That is why Marketing appears inside the business-colored Opus block here even though it sat in the Humanities & Communication family on the original grouped page.",
                    paragraphs: [
                        "This alternate view is about college membership and ordering, not about redefining the grouped-major buckets themselves."
                    ]
                },
                {
                    id: "college-limits-caveats",
                    title: "Limits / caveats",
                    tag: "Limits",
                    note: "This page is an alternate visual organization of the same grouped-major transition structure.",
                    rule: "Because the page prioritizes college blocks, some grouped-major labels will appear in a different visual family than they do on the original grouped dashboard.",
                    paragraphs: [
                        "The incoming-only Pre-Professional/Undeclared bucket still does not have a mirrored graduating block in the current data."
                    ]
                }
            ],
            colleges: {
                ocb: {
                    baseId: "college-ocb",
                    title: "Opus College of Business",
                    tag: "Large Group",
                    rule: "This college block collects the grouped-major buckets that this alternate view assigns to Opus College of Business, including Marketing in the college-colored version."
                },
                cas: {
                    baseId: "college-cas",
                    title: "College of Arts and Sciences",
                    tag: "Large Group",
                    rule: "This block collects grouped-major buckets assigned to the College of Arts and Sciences, mixing humanities, social science, science, and computing by college rather than by the original family colors."
                },
                other: {
                    baseId: "college-other",
                    title: "Other / Undeclared",
                    tag: "Large Group",
                    rule: "This block contains the incoming-only undeclared and pre-professional bucket, so it has no mirrored graduating college block."
                },
                educ: {
                    baseId: "college-educ",
                    title: "School of Education",
                    tag: "Large Group",
                    rule: "This block keeps the education bucket together under the School of Education in the college-colored view."
                },
                coh: {
                    baseId: "college-coh",
                    title: "Morrison Family College of Health",
                    tag: "Large Group",
                    rule: "This block keeps the health-science bucket together under the Morrison Family College of Health."
                },
                soe: {
                    baseId: "college-soe",
                    title: "School of Engineering",
                    tag: "Large Group",
                    rule: "This block keeps engineering grouped majors together under the School of Engineering."
                }
            },
            groups: groupedGroupDocs
        }
    };
}());
