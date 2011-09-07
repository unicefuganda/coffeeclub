from django.db.models.signals import post_syncdb
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from poll.models import *
from rapidsms_xforms.models import XFormField, XForm, XFormSubmission, dl_distance, xform_received, XFormFieldConstraint
from script.models import *

XFORMS = (
    ('', 'coffee', ',;:*.\\s"', 'coffee order', 'An order for coffee'),
)

XFORM_FIELDS = {
    'coffee':[
            ('cups', 'int', 'Number of cups of coffee', True),
            ('coffee_type', 'text', 'Type of coffee', False),
     ],
}

models_created = []
structures_initialized = False

def init_structures(sender, **kwargs):
    global models_created
    global structures_initialized
    models_created.append(sender.__name__)
    required_models = ['eav.models', 'rapidsms_xforms.models', 'poll.models', 'script.models', 'django.contrib.auth.models']
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        required_models.append('django.contrib.sites.models')
    if 'authsites' in settings.INSTALLED_APPS:
        required_models.append('authsites.models')
    for required in required_models:
        if required not in models_created:
            return
    if not structures_initialized:
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            site_id = getattr(settings, 'SITE_ID', 1)
            Site.objects.get_or_create(pk=site_id, defaults={'domain':'rapidcoffee.com'})
        init_groups()
        init_xforms(sender)
        init_autoreg(sender)
        structures_initialized = True

def init_groups():
    for g in ['Waiters', 'T4D', 'Child Protection', 'Wash', 'Education', 'Other Coffee People']:
        Group.objects.get_or_create(name=g)

def init_xforms(sender, **kwargs):
    init_xforms_from_tuples(XFORMS, XFORM_FIELDS)

def init_xforms_from_tuples(xforms, xform_fields):
    user, created = User.objects.get_or_create(username='admin')
    xform_dict = {}
    for keyword_prefix, keyword, separator, name, description in xforms:
        form, created = XForm.objects.get_or_create(
            keyword=keyword,
            keyword_prefix=keyword_prefix,
            defaults={
                'name':name,
                'description':description,
                'response':'',
                'active':True,
                'owner':user,
                'site':Site.objects.get_current(),
                'separator':separator,
                'command_prefix':'',
            }
        )
        if created:
            order = 0
            form_key = "%s%s" % (keyword_prefix, keyword)
            attributes = xform_fields[form_key]
            for command, field_type, description, required in attributes:
                xformfield, created = XFormField.objects.get_or_create(
                    command=command,
                    xform=form,
                    defaults={
                        'order':order,
                        'field_type':field_type,
                        'type':field_type,
                        'name':description,
                        'description':description,
                    }
                )
                if required:
                    xformfieldconstraint, created = XFormFieldConstraint.objects.get_or_create(
                        field=xformfield,
                        defaults={
                            'type':'req_val',
                             'message':("Expected %s, none provided." % description)
                        }
                )
                order = order + 1
            xform_dict[form_key] = form
    return xform_dict

def init_autoreg(sender, **kwargs):
    script, created = Script.objects.get_or_create(
            slug="coffee_autoreg", defaults={
            'name':"Coffee club subscription autoregistration script"})
    if created:
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            script.sites.add(Site.objects.get_current())
        user, created = User.objects.get_or_create(username="admin")

        script.steps.add(ScriptStep.objects.create(
            script=script,
            message="Welcome to the Coffee Club. The information you provide will be used to register you as a member of the club.",
            order=0,
            rule=ScriptStep.WAIT_MOVEON,
            start_offset=0,
            giveup_offset=60,
        ))
        name_poll = Poll.objects.create(\
            name='coffee_drinker', \
            user=user,
            type=Poll.TYPE_TEXT, \
            question='What is your name?', \
            default_response=''
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=name_poll,
            order=1,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=0,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        department_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_department',
            question='Which department are you (give name of department e.g \"T4D, WASH or Education\")?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=department_poll,
            order=2,
            rule=ScriptStep.STRICT_MOVEON,
            start_offset=0,
            retry_offset=86400,
            num_tries=1,
            giveup_offset=86400,
        ))
        extension_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_extension',
            question='What is your office telephone extension number?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=extension_poll,
            order=3,
            rule=ScriptStep.RESEND_MOVEON,
            start_offset=0,
            retry_offset=86400,
            num_tries=1,
            giveup_offset=86400,
        ))
        email_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_email',
            question='What is your email address?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=email_poll,
            order=4,
            rule=ScriptStep.RESEND_MOVEON,
            start_offset=0,
            retry_offset=86400,
            num_tries=1,
            giveup_offset=86400,
        ))
        standardcoffee_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_standard_type',
            question='Which is your favorite coffee (cappuccino, expresso)?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=standardcoffee_poll,
            order=5,
            rule=ScriptStep.RESEND_MOVEON,
            start_offset=0,
            retry_offset=86400,
            num_tries=1,
            giveup_offset=86400,
        ))
        milktype_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_milktype',
            question='Which milk type do you prefer (goat, cow)?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=milktype_poll,
            order=6,
            rule=ScriptStep.RESEND_MOVEON,
            start_offset=0,
            retry_offset=86400,
            num_tries=1,
            giveup_offset=86400,
        ))
        running_order_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_running_order',
            question='Would you like to place a running order (If Yes, send us the days e.g Mon, Tue, Wed if No, Ignore this question)?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=running_order_poll,
            order=7,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=0,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        own_cup_poll = Poll.objects.create(
            user=user, \
            type='yn', \
            name='coffee_own_cup',
            question='Do you prefer to use your own personal cup (Yes or No)?', \
            default_response='', \
        )
        own_cup_poll.add_yesno_categories()
        yes_category = own_cup_poll.categories.get(name='yes')
        yes_category.name = 'owncup'
        yes_category.response = "We received your response as 'yes',please have your personal cup ready for pickup whenever you order for coffee."
        yes_category.priority = 4
        yes_category.color = '99ff77'
        yes_category.save()
        no_category = own_cup_poll.categories.get(name='no')
        no_category.response = "We received your response as 'no',all your coffee orders will be served in our cups."
        no_category.name = 'nocup'
        no_category.priority = 1
        no_category.color = 'ff9977'
        no_category.save()
        unknown_category = own_cup_poll.categories.get(name='unknown')
        unknown_category.default = False
        unknown_category.priority = 2
        unknown_category.color = 'ffff77'
        unknown_category.save()
        unclear_category = Category.objects.create(
            poll=own_cup_poll,
            name='unclear',
            default=True,
            color='ffff77',
            response='We have recorded but did not understand your response,please repeat (with a yes or no response)',
            priority=3
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=own_cup_poll,
            order=8,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=0,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        other_notes_poll = Poll.objects.create(
            user=user, \
            type=Poll.TYPE_TEXT, \
            name='coffee_other_notes',
            question='Any extra special instructions concerning your coffee orders?', \
            default_response='', \
        )
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=other_notes_poll,
            order=9,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=0,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        script.steps.add(ScriptStep.objects.create(
            script=script,
            message="Thank you for registering as a new member of the coffee club, remember to deposit funds in your new account with Anna Spindler in Supply Unit.",
            order=10,
            rule=ScriptStep.WAIT_MOVEON,
            start_offset=60,
            giveup_offset=0,
        ))
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            for poll in [name_poll, department_poll, extension_poll, standardcoffee_poll, milktype_poll, running_order_poll, own_cup_poll, other_notes_poll]:
                poll.sites.add(Site.objects.get_current())

post_syncdb.connect(init_structures, weak=False)
