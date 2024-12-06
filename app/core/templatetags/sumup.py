from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def generate_sumup_url(donation):
    return f'''
        sumupmerchant://pay/1.0?
        affiliate-key={settings.SUMUP_AFFILIATE_KEY}
        &app-id=com.sumup.appswitch
        &amount={donation.amount}
        &currency=GBP
        &title=Challenge%20Adventure%20Group%20Car%20Wash
        &callbacksuccess=https://cagwash.challengeadventure.org/administration/{donation.id}/payment-complete/
        &callbackfail=https://cagwash.challengeadventure.org/administration/{donation.id}/payment-complete/
        &skip-screen-success=true
    '''.replace(
        ' ', ''
    )
