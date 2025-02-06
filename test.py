import re
from bs4 import BeautifulSoup

def parse_table_to_dict(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []
    is_contact_info = False
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) == 1 and 'colspan' in cols[0].attrs:
            is_contact_info = True
        if len(cols) == 2 and 'colspan' not in cols[0].attrs and is_contact_info:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            data.append({
                "area": "contact_information",
                "field": key,
                "field_value": value,
            })
        elif len(cols) == 2 and 'colspan' not in cols[0].attrs and not is_contact_info:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            data.append({
                "area": "comercial_establishment",
                "field": key,
                "field_value": value,
            })
            
    return data

def has_registration_number(data, registration_number):
    for item in data:
        if item['field'] == 'Numero de Matricula' and item['field_value'] == registration_number:
            return True
    return False

if __name__ == '__main__':
    html = """
<table class="table">
                            <tbody>
                                <tr>
                                    <td class="c-blue" style="width:35%;">Numero de Matricula</td>
                                    <td>1923339</td>
                                </tr>
                                    <tr>
                                        <td class="c-blue">Último Año Renovado</td>
                                        <td>2009</td>
                                    </tr>
                                                                    <tr>
                                        <td class="c-blue">Fecha de Renovacion</td>
                                        <td>20090820</td>
                                    </tr>
                                <tr>
                                    <td class="c-blue">Fecha de Matricula</td>
                                    <td>20090820</td>
                                </tr>
                                <tr>
                                    <td class="c-blue">Fecha de Vigencia</td>
                                        <td></td>
                                </tr>
                                <tr>
                                    <td class="c-blue">Estado de la matricula</td>
                                    <td>CANCELADA</td>
                                </tr>
                                    <tr>
                                        <td class="c-blue">Fecha de Cancelación</td>
                                        <td>20100107</td>
                                    </tr>
                                                                                                <tr>
                                    <td class="c-blue">Tipo de Organización</td>
                                    <td>PERSONA NATURAL</td>
                                </tr>
                                <tr>
                                    <td class="c-blue">Categoria de la Matricula</td>
                                    <td>PERSONA NATURAL</td>
                                </tr>
                                <tr>
                                    <td class="c-blue">Fecha Ultima Actualización</td>
                                    <td></td>
                                </tr>




                                    <tr><td colspan="2"><h3> Información de Contacto</h3></td></tr>
                                    <tr>
                                        <td class="c-blue">Municipio Comercial &nbsp;</td>
                                        <td>BOGOTA, D.C. &nbsp;/ BOGOTA</td>
                                    </tr>
                                    <tr>
                                        <td class="c-blue">Dirección Comercial &nbsp;</td>
                                        <td>CL 68 B NO. 76-49</td>
                                    </tr>
                                    <tr>
                                        <td class="c-blue">Teléfono Comercial &nbsp;</td>
                                        <td>5401376 &nbsp; 0000000 &nbsp; </td>
                                    </tr>
                                    <tr><td class="c-blue">Municipio Fiscal &nbsp;</td><td>BOGOTA, D.C. &nbsp;/ BOGOTA</td></tr>
                                    <tr>
                                        <td class="c-blue">Dirección Fiscal &nbsp;</td>
                                        <td>CL 68 B NO. 76-49</td>
                                    </tr>
                                    <tr>
                                        <td class="c-blue">Teléfono Fiscal &nbsp;</td>
                                        <td>5401376 &nbsp; 0000000 &nbsp; </td>
                                    </tr>
                                    <tr>
                                        <td class="c-blue">Correo Electrónico Comercial&nbsp;</td>
                                        <td></td>
                                    </tr>
                                    <tr>
                                        <td class="c-blue">Correo Electrónico Fiscal&nbsp;</td>
                                        <td></td>
                                    </tr>
                            </tbody>
                        </table>
    """
    resultado = parse_table_to_dict(html)
    print(resultado)
