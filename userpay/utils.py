from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

one = [ "", "one ", "two ", "three ", "four ", 
        "five ", "six ", "seven ", "eight ", 
        "nine ", "ten ", "eleven ", "twelve ", 
        "thirteen ", "fourteen ", "fifteen ", 
        "sixteen ", "seventeen ", "eighteen ", 
        "nineteen "]; 
  
# strings at index 0 and 1 are not used,  
# they is to make array indexing simple 
ten = [ "", "", "twenty ", "thirty ", "forty ", 
        "fifty ", "sixty ", "seventy ", "eighty ", 
        "ninety "]; 
  
# n is 1- or 2-digit number 
def numToWords(n, s): 
  
    str = ""; 
      
    # if n is more than 19, divide it 
    if (n > 19): 
        str += ten[n // 10] + one[n % 10]; 
    else: 
        str += one[n]; 
  
    # if n is non-zero 
    if (n): 
        str += s; 
  
    return str; 
  
# Function to print a given number in words 
def convertToWords(n): 
  
    # stores word representation of given  
    # number n 
    out = ""; 
  
    # handles digits at ten millions and  
    # hundred millions places (if any) 
    out += numToWords((n // 10000000),  
                            "crore "); 
  
    # handles digits at hundred thousands  
    # and one millions places (if any) 
    out += numToWords(((n // 100000) % 100), 
                                   "lakh "); 
  
    # handles digits at thousands and tens  
    # thousands places (if any) 
    out += numToWords(((n // 1000) % 100),  
                             "thousand "); 
  
    # handles digit at hundreds places (if any) 
    out += numToWords(((n // 100) % 10),  
                            "hundred "); 
  
    if (n > 100 and n % 100): 
        out += "and "; 
  
    # handles digits at ones and tens 
    # places (if any) 
    out += numToWords((n % 100), ""); 
  
    return out; 