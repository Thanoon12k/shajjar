"""Load Shajjar starter content.

    python manage.py seed_shajjar          # real starter content (species, sites, stories, law)
    python manage.py seed_shajjar --demo   # + fictional demo users/requests/trees/reports/campaigns

Idempotent: re-running updates records instead of duplicating them.
Site locations are approximate and should be corrected by the team from the admin.
"""
import os
import random
import secrets
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from campaigns.models import Campaign, CampaignParticipant
from content.models import ArticleCategory, ContentArticle, ContributionGoal, ContributionMethod
from core.services import notify
from planting.models import PlantingBatch, PlantingSite
from reports.models import EnvironmentalReport
from species.models import TreeSpecies
from tree_requests.models import TreeRequest
from trees.models import Health, Tree, TreeUpdate

FB = "https://www.facebook.com/"
DEMO_PASSWORD = "shajjar-demo-2026"

SPECIES = [
    dict(arabic_name="النبك (السدر)", english_name="Christ's thorn jujube", scientific_name="Ziziphus spina-christi", emoji="🌳",
         heat_tolerance=5, drought_tolerance=5, water_requirement=1, growth_speed=4, shade_level=4,
         suitable_for_streets=True, suitable_for_gardens=True, suitable_for_public_spaces=True, suitable_for_farms=True, bird_friendly=True, fruitful=True,
         description="الصنف المقاوم للمكان الصعب. يتحمل حرارة صيف الموصل والجفاف، ويعطي ظل كثيف وثمر (النبق) تحبه الطيور. اخترناه لشارع الشلالات وغابة الموصل الأيمن وشارعي القادسية والتحرير.",
         notes="يحتاج سقي منتظم أول سنتين فقط، وبعدها يعتمد على نفسه تقريباً."),
    dict(arabic_name="الألبيزيا", english_name="Siris tree", scientific_name="Albizia lebbeck", emoji="⛱️",
         heat_tolerance=4, drought_tolerance=4, water_requirement=2, growth_speed=5, shade_level=5,
         suitable_for_streets=True, suitable_for_gardens=True, suitable_for_public_spaces=True, bird_friendly=True,
         description="شكلها يشبه القبة أو المظلة، لهذا نحب نزرعها بالأماكن العامة. أثبتت إنها جيدة بالنمو رغم أجواء الصيف، وسريعة النمو — بغابة الأيمن وصلت أكثر من مترين بالشهر العاشر."),
    dict(arabic_name="الأثل", english_name="Athel tamarisk", scientific_name="Tamarix aphylla", emoji="🌲",
         heat_tolerance=5, drought_tolerance=5, water_requirement=1, growth_speed=4, shade_level=3,
         suitable_for_public_spaces=True, suitable_for_farms=True,
         description="من النباتات المحلية. ظهور نموه الطبيعي بغابة الموصل الأيمن دليل على صحة الخطوات. الطرفة والأثل مو نفس الشجرة بالمعنى التصنيفي الدقيق، لكن هم من نفس جنس Tamarix.",
         notes="ممتاز كمصدّ رياح حول البساتين والغابات."),
    dict(arabic_name="الرمان", english_name="Pomegranate", scientific_name="Punica granatum", emoji="🍎",
         heat_tolerance=4, drought_tolerance=4, water_requirement=2, growth_speed=3, shade_level=2,
         suitable_for_gardens=True, suitable_for_farms=True, fruitful=True, bird_friendly=True,
         description="أساس بساتين #شجّر بالبعاج والنمرود — بستان البعاج (2 دونم) صار مزهر ويثمر بعد سنة. باب رزق لأصحاب الأراضي الشباب."),
    dict(arabic_name="الزيتون", english_name="Olive", scientific_name="Olea europaea", emoji="🫒",
         heat_tolerance=4, drought_tolerance=5, water_requirement=1, growth_speed=2, shade_level=3,
         suitable_for_gardens=True, suitable_for_farms=True, suitable_for_public_spaces=True, fruitful=True,
         description="شجرة معمّرة جداً وتتحمل العطش. بطيئة النمو لكن تعيش أجيال."),
    dict(arabic_name="التوت", english_name="White mulberry", scientific_name="Morus alba", emoji="🫐",
         heat_tolerance=4, drought_tolerance=3, water_requirement=2, growth_speed=4, shade_level=5,
         suitable_for_gardens=True, suitable_for_farms=True, suitable_for_public_spaces=True, bird_friendly=True, fruitful=True,
         description="ظل واسع وثمر للطيور والناس. شجرة تراثية بحدائق بيوت الموصل."),
    dict(arabic_name="السرو", english_name="Mediterranean cypress", scientific_name="Cupressus sempervirens", emoji="🌲",
         heat_tolerance=4, drought_tolerance=4, water_requirement=1, growth_speed=3, shade_level=1,
         suitable_for_streets=True, suitable_for_gardens=True, suitable_for_public_spaces=True,
         description="قائمي الشكل ومناسب للجزرات الوسطية والمداخل والأسيجة الخضراء."),
    dict(arabic_name="البلوط العراقي", english_name="Brant's oak", scientific_name="Quercus brantii", emoji="🌰",
         heat_tolerance=3, drought_tolerance=4, water_requirement=1, growth_speed=1, shade_level=4,
         suitable_for_public_spaces=True,
         description="شجرة جبال شمال العراق الأصلية. بطيء جداً لكنه حجر أساس للغابات الطبيعية."),
    dict(arabic_name="اليوكالبتوس (الكالبتوز)", english_name="River red gum", scientific_name="Eucalyptus camaldulensis", emoji="🌴",
         heat_tolerance=5, drought_tolerance=3, water_requirement=3, growth_speed=5, shade_level=3,
         suitable_for_farms=True, suitable_for_public_spaces=True,
         description="سريع جداً ويتحمل الحر، لكنه شره للماء وجذوره قوية.",
         notes="لا ننصح بيه قرب البيوت والأرصفة والأنابيب؛ مناسب كمصد رياح بعيد عن البناء."),
]

# name, kind, city, district, lat, lng, species, organization, watering, date, total, alive, damaged, dead, status, featured, post, description
SITES = [
    ("غابة الحدباء", "forest", "الموصل", "جامعة الحدباء", 36.3905, 43.1455, ["النبك (السدر)", "الألبيزيا", "الأثل"], "جامعة الحدباء", "جامعة الحدباء", date(2024, 3, 1), 1000, 987, 0, 13, "active", True,
     "reel/1488972326338910/", "من مجموع 1000 شجرة بغابة الحدباء فقط 13 شجرة تعرضت للتيبس بسبب الظروف، وأكيد راح يتم استبدال كل شجرة ماتت.\nمساحة جميلة لطلاب جامعة الحدباء — «راح نتعب عليها… حتى يجي اليوم اللي أستظل تحت أشجار #شجّر»."),
    ("غابة الموصل الأيمن — أسوار البرج العاجي", "forest", "الموصل", "الجانب الأيمن", 36.3570, 43.1175, ["النبك (السدر)", "الألبيزيا", "الأثل"], "مؤسسة مثابرون للخير للبيئة والتنمية", "شعبة الغابات", date(2024, 10, 1), 0, 0, 0, 0, "active", True,
     "reel/2537246563387430/", "الموقع اللي أكله الحريق قبل سنوات ورجعت له الحياة. التنوع بالأشجار مدروس: كل نوع يستفاد من العناصر الغذائية بطريقة مختلفة وتتبادل المنفعة. حتى الشجرة اللي تيبست من الساق رجعت تنمو من جديد، وبدأ يظهر نمو طبيعي للأثل."),
    ("غابة الشورة", "forest", "الشورة", "ناحية الشورة", 35.9830, 43.2010, ["النبك (السدر)", "الألبيزيا"], "مؤسسة مثابرون للخير للبيئة والتنمية", "بلدية ناحية الشورة", date(2024, 11, 1), 0, 0, 0, 0, "active", False,
     "permalink.php?story_fbid=pfbid02zH1sEZgKZBkWZmnfrztwmqn5ziKr8jZAweDzgjFDGqodEbSrk5ruGN8UgFKjSdcEl&id=100088411089966", "زرعت ضمن #شجّر الموسم السابق، وكادر بلدية الشورة يسقيها ويرعاها بشكل يومي."),
    ("شارع الشلالات", "street", "الموصل", "الشلالات", 36.3805, 43.1500, ["النبك (السدر)"], "بالتعاون مع شعبة الجزرات", "شعبة الجزرات", date(2026, 3, 1), 0, 0, 0, 0, "active", True,
     "reel/1419359280080320/", "اختيار الصنف المقاوم بالمكان الصعب — النبك. الزراعة بالتعاون مع شعبة الجزرات، وبعد ستة أشهر النتائج واضحة بفضل كادر البلدية."),
    ("بستان رمان البعاج", "orchard", "البعاج", "البعاج", 36.0360, 41.7250, ["الرمان"], "مؤسسة مثابرون للخير للبيئة والتنمية", "صاحب البستان", date(2025, 3, 1), 0, 0, 0, 0, "active", True,
     "reel/1046989738049251/", "بستان بمساحة 2 دونم بأشجار الرمان، زرع قبل عام ضمن #شجّر وصار مزهر ويثمر. البعاج راح تتحول لخضراء بجهود الأهالي وبلدية البعاج."),
    ("بستان النمرود", "orchard", "النمرود", "النمرود", 36.0980, 43.3290, ["الرمان"], "مؤسسة مثابرون للخير للبيئة والتنمية", "صاحب البستان", date(2025, 3, 1), 0, 0, 0, 0, "active", False,
     "permalink.php?story_fbid=pfbid0LyEhCL1oCad2UJTdB3JckziDjzuPg7B7jaoenKpYx3t13tmqcEHYwe1i7SLoryaNl&id=100088411089966", "بستان آخر ضمن #شجّر والنمو جيد — باب رزق لصاحبه مستقبلاً ومساحة خضراء تليق به."),
    ("أشجار حي التعليم", "neighborhood", "الموصل", "حي التعليم", 36.3640, 43.1720, ["النبك (السدر)", "الألبيزيا"], "#شجّر مع أهالي الحي", "الأهالي وأصحاب المحلات", date(2024, 4, 1), 0, 0, 0, 0, "active", False,
     "permalink.php?story_fbid=pfbid09MdQd3AoBLfh2wa6pqUcusaigEB8HeZVAa9AjofAUFTWG3w58pjbdXwa2SZ41bsml&id=100088411089966", "قبل وبعد — تعاون مشترك ويا الأهالي، وجهدهم مستمر برعاية الأشجار لحد هذه اللحظة."),
    ("الشارع الأخضر — حي الغفران", "street", "الموصل", "حي الغفران", 36.3295, 43.1905, ["الألبيزيا", "السرو"], "#شجّر", "بلدية الموصل", date(2026, 2, 1), 0, 0, 0, 0, "needs_attention", False,
     "reel/1710852196852181/", "بعد انتهاء أعمال التبليط والأرصفة صار المجال نشتغل عليه حتى يتحول المكان لأخضر."),
    ("حي دوميز — جامع نور الإسلام", "neighborhood", "الموصل", "حي دوميز", 36.3480, 43.2010, ["النبك (السدر)"], "#شجّر مع الجامع وأهالي الحي", "جامع نور الإسلام وأهالي الحي", date(2025, 3, 1), 0, 0, 0, 0, "active", False,
     "reel/1996574657657969/", "الري والتنقيط والرعاية من الجامع وشباب الحي المبدعين — بعد كم سنة يتحول لمكان جميل."),
    ("حي الصحة", "neighborhood", "الموصل", "حي الصحة", 36.3320, 43.1060, ["الألبيزيا"], "#شجّر", "ذنون — متطوع من الحي", date(2025, 4, 1), 0, 0, 0, 0, "active", False,
     "reel/1015792134414013/", "الشاب ذنون يسقي الأشجار يومياً — ببركة مساهمة أهالي الموصل نحقق هدفنا بموصل خضراء."),
    ("حي حمورابي", "neighborhood", "الموصل", "حي حمورابي", 36.3950, 43.1780, ["الألبيزيا", "النبك (السدر)"], "#شجّر", "الأهالي", date(2025, 10, 1), 0, 0, 0, 0, "needs_attention", False,
     "reel/1302958431657806/", "من الأحياء الحديثة اللي تحتاج تشجير — زرعنا مجموعة أشجار ونتابع نموها."),
]

STORIES = [
    ("غابة الحدباء: 987 من 1000", "reel/1488972326338910/", "من مجموع 1000 شجرة بغابة الحدباء فقط 13 شجرة تعرضت للتيبس بسبب الظروف. أكيد راح يتم استبدال كل شجرة تعرضت للموت، المهم إن غابة الحدباء من زرعها فكّر بالمستقبل."),
    ("من رماد إلى غابة", "permalink.php?story_fbid=pfbid036jw6y63Wowhmi6mPeucV5JPAj3MaUMGhHksVf4MSbZLrvjpgKkjT1GMgzwWzA5Epl&id=100088411089966", "قبل وبعد لنفس المكان — قبل إعادة زراعة كل شبر بغابة الموصل الموقع اللي احترق. الحمدلله، اللي يتذكر كيف تحولت إلى رماد وهسه كيف صارت خضراء مليانة أشجار."),
    ("النبك بالمكان الصعب", "reel/1419359280080320/", "شارع الشلالات، اختيار الصنف المقاوم بالمكان الصعب — أشجار النبك. تمت الزراعة ضمن #شجّر بالتعاون مع شعبة الجزرات قبل ستة أشهر، واليوم بفضل جهود كادر البلدية النتائج أمامكم."),
    ("أيادي الخير بحي الميثاق", "reel/998324763237650/", "شاب من حي الميثاق بشكل يومي يسقي الشجرة أمام محل عمله ويوفر لها احتياجها المائي. أيادي الخير بكل مكان موجودة، وبسببها تزدهر مدننا."),
    ("بستان عبدالله", "permalink.php?story_fbid=pfbid026CUwdBDgi4HqQkFSmF5v6rAsoWQ387iaTAjFUyqHfHPbhdQnzftzWSWFA9q8VxFGl&id=100088411089966", "عبدالله طالب جامعي، مو بس شاطر بالدراسة — شاطر بالزراعة، وهذا البستان نتيجة تعبه. الأشجار علينا من مثابرون، والتعب والرعاية عليه."),
    ("الألبيزيا: المظلة الخضراء", "reel/28071105625872870/", "شجرة الألبيزيا، لهذا أحب زراعتها بالأماكن العامة لأن شكلها يشبه القبة أو المظلة. أثبتت إنها جيدة بالنمو رغم أجواء الصيف، وسريعة النمو ومناسبة للتشجير."),
    ("ثقافة تبدأ من البيت", "permalink.php?story_fbid=pfbid0vBvPCZQffCXicNvXnqxjyQYEzWwsYXTuTbK88UrK5aiNoBd7AH8qVyQzCkyxyhvVl&id=100088411089966", "تنولد الثقافة من الأهل بعد ما يعلمون أطفالهم عالصح. الصديق خالد البدراني يأخذ أولاده ويخليهم بإيديهم يسقون الأشجار على شارع بغداد بشكل يومي."),
    ("قرية الحمزة بعد سنتين", "reel/871819192478980/", "تصوّر هالشارع بقرية الحمزة زرعناه قبل سنتين، واليوم هالجمال. وأنا أتصورها بعد كم عام شلون تغطي المكان."),
]

ARTICLES = [
    ("tree-care", "مو كل شجرة تعيش ببلدك", "كل نوع وصنف له بيئته الخاصة — شلون تختار الصنف المناسب للموصل.",
     "ما كل شجرة تشوفها ببقية البلدان يعني تعيش ببلدك. كل نوع وصنف له بيئته الخاصة.\n\nقبل ما تزرع اسأل ثلاث أسئلة:\n1) وين راح أزرع؟ رصيف، حديقة بيت، بستان، أو مكان عام.\n2) شكد الشمس قوية؟ أغلب شوارع الموصل تتعرض لشمس قوية طول اليوم بالصيف.\n3) شكد الماء متوفر؟ إذا الماء قليل اختار أنواع تتحمل العطش مثل النبك والأثل والزيتون.\n\nجرّب موسوعة «شنو أزرع؟» على المنصة حتى تشوف الأنواع مرتبة حسب ظروفك."),
    ("tree-care", "أول سنتين من عمر الشجرة", "السقي والحماية بالسنتين الأولى هي اللي تحدد إذا الشجرة تعيش.",
     "الشتلة بأول سنتين تحتاجك أكثر شي:\n\n• السقي: بالصيف كل يومين إلى ثلاث أيام، سقي عميق الصبح بدري أو بعد العصر. بالشتاء حسب المطر.\n• الحوض: سوّي حوض حول الشجرة حتى يجمع الماء ولا يروح للشارع.\n• الحماية: سياج بسيط يحميها من الحيوانات والدعس.\n• لا تقلّم بالسنة الأولى إلا الأغصان اليابسة.\n• صوّرها كل كم شهر وارفع الصورة على المنصة — هيچ نعرف إذا تحتاج مساعدة."),
    ("awareness", "شجرة واحدة… وأثر لسنين", "ليش التشجير بالموصل مو رفاهية؟",
     "الشجرة تخفف حرارة الشارع، تقلل الغبار، تعطي ظل للمارة والمراجعين، وملجأ للطيور. الشوارع اللي زرعت ضمن #شجّر قبل أربع وخمس سنوات صارت اليوم الفرق واضح بيها.\n\nالهدف مستقبلي: مدينة خضراء. وكل واحد يكدر يساهم — شجرة أمام البيت أو المحل، أو سقي شجرة موجودة."),
]

LAW = [
    ("trees-law", "⚖️", "قطع الأشجار", [
        ("ما الحالات الممنوعة؟", "حسب ما نشرته حملة #شجّر نقلاً عن قانون حماية وتحسين البيئة رقم 27 لسنة 2009 (المادة 20): يُحظر قطع الأشجار المعمّرة في المناطق العامة داخل المدن إلا بإذن أصولي — والمقصود بالمعمّرة ما بلغ عمره 30 سنة فأكثر. كما يُحظر قطع أشجار الغابات دون ترخيص.\n\nالقاعدة الذهبية: لا تقطع أي شجرة بدون موافقة رسمية من الجهة المختصة (البلدية / مديرية البيئة / مديرية الزراعة)."),
        ("ما العقوبة؟", "حسب المنشور نفسه، المادة 34 من القانون: الحبس مدة لا تقل عن 3 أشهر أو غرامة من مليون إلى 20 مليون دينار أو كلتا العقوبتين، مع عدم الإخلال بأي عقوبة أشد ينص عليها قانون آخر."),
        ("لمن أقدّم البلاغ؟", "• وثّق التجاوز بصورة أو فيديو مع الموقع والوقت.\n• بلّغ على منصة #شجّر من صفحة «بلّغ» — الفريق يتابع ويحيل البلاغ.\n• تكدر تراجع مديرية البيئة في نينوى أو شرطة البيئة أو البلدية المختصة.\n• بالحرائق: اتصل بالدفاع المدني 115 فوراً."),
    ]),
    ("wildlife-law", "🐦", "الصيد الجائر والحياة البرية", [
        ("الحيوانات المحمية", "حسب ما نشرته الحملة عن قانون حماية الحيوانات البرية رقم 17 لسنة 2010: تُعد الحيوانات البرية ثروة وطنية، ويُحظر صيد الأنواع المحرّم صيدها."),
        ("وسائل الصيد الممنوعة", "يُمنع استخدام وسائل الإبادة الجماعية مثل الشباك والفخاخ والسموم، ومطاردة الحيوانات والطيور البرية بالسيارات ووسائل النقل، وجمع بيض الطيور أو تخريب أعشاشها. صيد أسراب طيور القطا بأعداد كبيرة بالبعاج وتلعفر والحضر والقيارة من أخطر التجاوزات المستمرة."),
        ("مواسم الصيد والإجازة", "نصّت المادة (6/ثانياً) على تنظيم منح إجازة صيد الحيوانات البرية. مواسم الصيد والأنواع المسموحة تحددها الجهات المختصة — راجعها قبل أي صيد."),
        ("طريقة التبليغ", "صوّر (بدون تعريض نفسك للخطر)، حدد الموقع، وبلّغ من صفحة «بلّغ» باختيار «صيد جائر» أو «اعتداء على الحياة البرية»."),
    ]),
]

GOALS = [
    ("🌱", "كلفة زراعة شجرة", "شتلة + نقل + زراعة + سقي أول شهر", None),
    ("🌳", "دعم حملة", "شتلات وأدوات ونقل لحملة تشجير حي كامل", None),
    ("💧", "دعم منظومة ري", "أنابيب تنقيط وخزانات للغابات والبساتين", None),
]


class Command(BaseCommand):
    help = "Seed Shajjar starter content (and optional demo data with --demo)."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="Also create fictional demo users, requests, trees, reports and campaigns.")

    @transaction.atomic
    def handle(self, *args, demo=False, **opts):
        sp = self.seed_species()
        sites = self.seed_sites(sp)
        self.seed_content()
        if demo:
            self.seed_demo(sp, sites)
        self.stdout.write(self.style.SUCCESS("✓ Shajjar seed complete" + (" (with demo data)" if demo else "")))

    def seed_species(self):
        out = {}
        for d in SPECIES:
            obj, _ = TreeSpecies.objects.update_or_create(arabic_name=d["arabic_name"], defaults=d)
            out[obj.arabic_name] = obj
        return out

    def seed_sites(self, sp):
        out = []
        for (name, kind, city, district, lat, lng, species, org, water, d, total, alive, damaged, dead, status, featured, post, desc) in SITES:
            site, created = PlantingSite.objects.get_or_create(
                name=name,
                defaults=dict(kind=kind, city=city, district=district, latitude=lat, longitude=lng, organization=org,
                              watering_entity=water, planting_date=d, total_trees=total, alive_trees=alive,
                              damaged_trees=damaged, dead_trees=dead, status=status, is_featured=featured,
                              source_url=FB + post, description=desc),
            )
            if created:
                site.species.set([sp[s] for s in species])
            out.append(site)
        return out

    def seed_content(self):
        field, _ = ArticleCategory.objects.update_or_create(slug="field", defaults=dict(name="من الميدان", icon="📣", sort_order=0))
        cats = {
            "tree-care": ArticleCategory.objects.update_or_create(slug="tree-care", defaults=dict(name="رعاية الأشجار", icon="🌱", sort_order=1))[0],
            "awareness": ArticleCategory.objects.update_or_create(slug="awareness", defaults=dict(name="توعية بيئية", icon="🌍", sort_order=2))[0],
        }
        now = timezone.now()
        for i, (title, post, body) in enumerate(STORIES):
            url = FB + post
            ContentArticle.objects.update_or_create(
                slug=slugify(title, allow_unicode=True),
                defaults=dict(title=title, summary=body[:290], body=body + "\n\n— أنس الطائي، #شجّر", category=field, source_url=url, published_at=now - timedelta(days=i * 3)),
            )
        for i, (cat, title, summary, body) in enumerate(ARTICLES):
            ContentArticle.objects.update_or_create(
                slug=slugify(title, allow_unicode=True),
                defaults=dict(title=title, summary=summary, body=body, category=cats[cat], published_at=now - timedelta(days=i * 5 + 1)),
            )
        for order, (slug, icon, name, items) in enumerate(LAW):
            cat, _ = ArticleCategory.objects.update_or_create(slug=slug, defaults=dict(name=name, icon=icon, is_legal=True, sort_order=10 + order))
            for j, (title, body) in enumerate(items):
                ContentArticle.objects.update_or_create(
                    slug=slugify(f"{name}-{title}", allow_unicode=True),
                    defaults=dict(title=title, body=body, category=cat, needs_legal_review=True, published_at=now - timedelta(minutes=j)),
                )
        for i, (icon, title, desc, amount) in enumerate(GOALS):
            ContributionGoal.objects.update_or_create(title=title, defaults=dict(icon=icon, description=desc, amount_iqd=amount, sort_order=i))
        if not ContributionMethod.objects.exists():
            ContributionMethod.objects.create(
                name="التواصل مع مؤسسة مثابرون",
                description="للمساهمة بالشتلات أو الحملات، تواصل مع المؤسسة مباشرة عبر صفحتها الرسمية.",
                instructions="تُضاف أرقام الحسابات الرسمية المعتمدة من قبل إدارة المؤسسة فقط من لوحة الإدارة.",
            )

    # ------------------------------------------------------------------ demo
    def seed_demo(self, sp, sites):
        rnd = random.Random(42)
        User = get_user_model()

        team_password = os.environ.get("SHAJJAR_TEAM_PASSWORD") or secrets.token_urlsafe(12)

        def user(email, name, role, district, staff=False, superuser=False):
            u, created = User.objects.get_or_create(email=email, defaults=dict(full_name=name, role=role, district=district, is_staff=staff, is_superuser=superuser, is_verified=True))
            if created:
                # staff accounts never get the public demo password
                u.set_password(team_password if staff else DEMO_PASSWORD)
                u.save()
                if staff:
                    self.stdout.write(f"  team login: {email} / {team_password}")
            return u

        admin = user("admin@shajjar.demo", "مدير المنصة", "super_admin", "", staff=True, superuser=True)
        sup = user("supervisor@shajjar.demo", "مشرف ميداني", "supervisor", "حي التعليم", staff=True)
        citizens = [
            user("citizen@shajjar.demo", "محمد أحمد", "citizen", "حي التعليم"),
            user("sara@shajjar.demo", "سارة يونس", "citizen", "حي الغفران"),
            user("omar@shajjar.demo", "عمر خالد", "citizen", "حي دوميز"),
        ]
        for args in [
            ("volunteer@shajjar.demo", "ثانون", "volunteer", "حي الزهور"),
            ("ali@shajjar.demo", "علي حسن", "volunteer", "حي الصحة"),
            ("noor@shajjar.demo", "نور محمود", "volunteer", "حي المثنى"),
        ]:
            user(*args)
        for i in range(24):
            user(f"vol{i}@shajjar.demo", f"متطوع {i + 1}", "volunteer", rnd.choice(["حي التعليم", "حي الغفران", "حي الصحة", "دوميز"]))

        # illustrative counts for sites the team hasn't filled yet
        for s in sites:
            if not s.total_trees:
                total = rnd.choice([120, 180, 240, 300, 450, 600, 850])
                dead = int(total * rnd.uniform(.02, .08))
                damaged = int(total * rnd.uniform(.02, .1)) if s.status == "needs_attention" else int(total * rnd.uniform(0, .04))
                s.total_trees, s.dead_trees, s.damaged_trees = total, dead, damaged
                s.alive_trees = total - dead
                s.save()
            if not s.batches.exists():
                for spc in s.species.all():
                    PlantingBatch.objects.create(planting_site=s, species=spc, quantity=max(1, s.total_trees // max(1, s.species.count())), planting_date=s.planting_date, responsible_entity=s.organization, watering_entity=s.watering_entity)

        if TreeRequest.objects.exists():
            return
        base = (36.3456, 43.1450)
        today = timezone.localdate()
        statuses = ["submitted", "under_review", "approved", "ready_for_distribution", "distributed", "planted", "planted", "rejected"]
        for i, st in enumerate(statuses):
            owner = citizens[i % 3]
            r = TreeRequest.objects.create(
                user=owner, location_type=rnd.choice(["home", "shop", "school", "mosque", "street"]), requested_tree_count=rnd.choice([2, 3, 5, 10]),
                latitude=round(base[0] + rnd.uniform(-.03, .04), 6), longitude=round(base[1] + rnd.uniform(-.03, .05), 6),
                address_description="عنوان تجريبي", district=owner.district, status=st, preferred_species=sp["النبك (السدر)"] if i % 2 else sp["الألبيزيا"],
                public_note="تم تحديد موعد الاستلام من مشتل المؤسسة." if st == "ready_for_distribution" else "",
                distribution_date=today + timedelta(days=5) if st == "ready_for_distribution" else None,
            )
            if st == "planted":
                for k in range(3):
                    planted = today - timedelta(days=184 + k * 90)
                    t = Tree.objects.create(species=r.preferred_species, request=r, owner=owner, latitude=r.latitude + k * 0.0002, longitude=r.longitude,
                                            location_label=f"{owner.district} – الموصل", planting_date=planted, height_cm=60 + k * 40,
                                            health_status=[Health.EXCELLENT, Health.GOOD, Health.NEEDS_CARE][k])
                    for m, (h, hs, note) in enumerate([(55, "good", "بدأت تطلع أوراق جديدة"), (95 + k * 20, "excellent" if k == 0 else "good", "السقي منتظم والحمد لله")]):
                        u = TreeUpdate(tree=t, user=owner, height_cm=h, health_status=hs, notes=note, verified=m == 0, verified_by=sup if m == 0 else None,
                                       created_at=timezone.now() - timedelta(days=(184 + k * 90) - 90 * (m + 1)))
                        u.save()
                        u.apply_to_tree()
                    notify(owner, f"🌳 صار {t.age_days // 30} أشهر على زراعة شجرتك", "صوّرها وخلي نشوف شلون كبرت.", type="tree", link=t.get_absolute_url(), obj=t)
        for site in sites[:4]:
            for k in range(6):
                Tree.objects.create(species=site.species.first(), site=site, planting_date=site.planting_date or today, height_cm=rnd.randint(80, 240),
                                    health_status=rnd.choice([Health.EXCELLENT, Health.GOOD, Health.GOOD, Health.NEEDS_CARE]), caretaker_name=site.watering_entity)

        reps = [
            ("tree_cutting", "قطع أشجار على الرصيف قرب ساحة الوكلاء", "under_review", "high"),
            ("illegal_hunting", "صيد أسراب طيور القطا بأعداد كبيرة", "forwarded", "high"),
            ("waste", "رمي نفايات على شارع رئيسي بجانب الأشجار المزروعة", "resolved", "normal"),
            ("fire", "حريق أعشاب قرب الغابة", "in_progress", "urgent"),
            ("green_area_destruction", "تجريف مساحة خضراء بأطراف المدينة", "submitted", "high"),
        ]
        for i, (cat, title, st, pr) in enumerate(reps):
            EnvironmentalReport.objects.create(
                reporter=citizens[i % 3], category=cat, title=title, description=title + " — بلاغ تجريبي للعرض فقط.",
                latitude=round(base[0] + rnd.uniform(-.04, .04), 6), longitude=round(base[1] + rnd.uniform(-.04, .04), 6),
                address_description="موقع تجريبي", status=st, priority=pr, public_note="تمت إحالة البلاغ لمديرية البيئة." if st == "forwarded" else "",
            )

        now = timezone.now()
        next_friday = now + timedelta(days=(4 - now.weekday()) % 7 or 7)
        next_friday = next_friday.replace(hour=8, minute=0, second=0, microsecond=0)
        camps = [
            ("تشجير حي الغفران", "حي الغفران", 36.3295, 43.1905, next_friday, 300, 40, "published"),
            ("زراعة غابة الحدباء — المرحلة الثانية", "جامعة الحدباء", 36.3905, 43.1455, next_friday + timedelta(days=7), 500, 60, "published"),
            ("الشارع الأخضر — شارع النبي شيت", "شارع النبي شيت", 36.3350, 43.1230, next_friday + timedelta(days=21), 200, 25, "published"),
            ("حملة البعاج الخضراء", "البعاج", 36.0360, 41.7250, now - timedelta(days=40), 400, 30, "completed"),
            ("تشجير حي التعليم", "حي التعليم", 36.3640, 43.1720, now - timedelta(days=90), 250, 30, "completed"),
        ]
        all_vols = list(User.objects.filter(role="volunteer"))
        for title, loc, lat, lng, start, target, need, st in camps:
            c = Campaign.objects.create(
                title=title, location_name=loc, latitude=lat, longitude=lng, start_date=start, end_date=start + timedelta(hours=4),
                registration_deadline=start - timedelta(hours=12), target_tree_count=target, volunteers_needed=need, status=st,
                organization="مؤسسة مثابرون للخير للبيئة والتنمية", created_by=admin,
                description=f"حملة تشجير ضمن #شجّر في {loc}.\n\n🧤 جيب وياك كفوف وقنينة ماء.\n🌳 الشتلات والأدوات علينا.\n\n(حملة تجريبية للعرض)",
            )
            for v in rnd.sample(all_vols, min(len(all_vols), rnd.randint(8, 18))):
                done = st == "completed"
                CampaignParticipant.objects.create(campaign=c, user=v, status="completed" if done else "registered",
                                                   trees_planted=rnd.randint(4, 12) if done else 0, volunteer_hours=4 if done else 0)
        self.stdout.write(f"  demo citizen logins: citizen@shajjar.demo / volunteer@shajjar.demo — password: {DEMO_PASSWORD}")
