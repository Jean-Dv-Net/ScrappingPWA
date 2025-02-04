import re
from bs4 import BeautifulSoup


if __name__ == '__main__':
    html = """
<div id="detalleguia">











<link rel="stylesheet" href="/css/font-all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
<style>
    span.message {
        color: black;
    }
</style>
<script>
    $(document).ready(function(){
            actualizardescarga();
    });
function actualizardescarga(){
    $.ajax({
	      	  type: 'POST',
	      	  url: '/administracion/action/verdescarga',
                  dataType:'json',
	      	  success: function(data){
                                var html='';
	        		console.log(data.cantidad);
                                var dawload=''
                                var pendiente=0;
                                var activos=0;
                                $.each( data.archivos, function( key, value ) {
                                    var idnim='li_'+value.id;
                                   if(value.fechafinal==null){
                                       html=html+"<li id="+idnim+"><a><i class='fas fa-ban fa-lg' style='color: #e61a22;'></i><span class='message'>"+value.nombre+"</span></a></li>";
                                       pendiente=pendiente+1;
                                    }else{
                                        activos=activos+1;
                                       html=html+"<li id="+idnim+"><a href='"+value.archivo+"' download onclick='validacion("+value.idpeticion+","+value.id+")'><i class='far fa-arrow-alt-circle-down fa-lg' style='color: #00377b;'></i><span class='message'>"+value.nombre+"</span></a></li>";
                                    }

                                });

                                if(pendiente>0){
                                    $("#resultado").addClass("badge badge-important");
                                }else{
                                    $("#resultado").addClass("badge");
                                }

                                if(activos>0){
                                    $("#resultado2").addClass("badge badge-success");
                                }else{
                                    $("#resultado2").addClass("badge");
                                }
                                $("#resultado").text(pendiente);
                                $("#resultado2").text(activos);
                                //"<li><a><span class='message'>".."</span></a></li>"
                                //console.log(activos);
                                $("#menu1").html(html);
	      	  },
	      	  error: function(){
	      	  	$("#resultado").addClass("badge badge-success");
	      	  },
	      	});
}
function validacion(idpeticion,id){
    $.ajax({
        type: 'POST',
        url: '/administracion/action/actualizardescarga',
        data:{idpeticion:idpeticion,id:id},
        dataType:'json',
        success: function(data){
           actualizardescarga();
        },
        error: function(){
              //$("#resultado").addClass("badge badge-success");
        },
      });
}
</script>


 <script>
$(document).ready(function(){
	
	var loadurl =  "/guiasdoc/action/buscarimagen/idguia/2380198462";
	var targ = $("#soloimagen");
	$.get(loadurl, function(data) {
		$(targ).html(data)
	});	

});
</script>

<table>
	<tbody><tr>
		<th>Guia :</th><td>2380198462</td>
		<th>Contrato :</th><td>15880056</td>
		<th>Orden :</th><td>15336</td>
	</tr>
</tbody></table>


<table style="width:100%; float:left; clear:left ">
    <tbody><tr>
            <td>
                <p style="float:left; margin-top:20px">Remitente</p>
                <table class="table table-bordered" style="width:100%; float:left; clear:left ">
                        <tbody><tr>
                                <th>Nombre :</th>
                                <td>UNE  </td>
                        </tr>
                        <tr>
                                <th>Identificacion :</th>
                                <td></td>
                        </tr>
                        <tr>
                                <th>Direccion :</th>
                                <td></td>
                        </tr>
                        <tr>
                                <th>Telefono :</th>
                                <td></td>
                        </tr>
                </tbody></table>
            </td>
            
           <td rowspan="2">
                <!--<div id="soloimagen" style="width:400px !important; height:325px !important; float:left; margin-left:150px"></div>-->

                           </td>
      </tr>  

 <tr>
          <td>    
             <p style="float:left; clear:left;">Destinatario</p><table class="table table-bordered " style="width:100%;  float:left; clear:left">
                        
                <tbody><tr>
                        <th>Nombre :
                        </th><td>ALBERTO EDUARDO CAMARGO VEGA</td>
                </tr>
                <tr>
                        <th>Cedula o Nit :
                        </th><td>1234890600</td>
                </tr>
                <tr>
                        <th>Origen / Destino :
                        </th><td>
                                <b>Medellin (Antioquia) /
                                Medellin (Antioquia)</b>
                                <br>
                                (<b>Subzona</b> :  
                                <b>Zona :</b>   )
                        </td>
                </tr>	
                <tr>
                        <th>Direccion :
                        </th><td>
                                <table>
                                        <tbody><tr>
                                                <td>kangusk8611@gmail.com</td>
                                        </tr>
                                                                                <tr>
                                                 
                                                        <td><a href="/guias/action/agregardireccion/idguia/2380198462">Actualizar Direccion</a></td>
                                                                                        </tr>
                                </tbody></table>
                        </td>
                </tr>
                <tr>
                        <th>Telefono :</th>
                        <td>
                                <table>
                                        <tbody><tr>
                                                <td>3128278546</td>
                                                <td></td>
                                        </tr>
                                                                                <tr>
                                                 
                                                        <td><a href="/guias/action/agregartelefono/idguia/2380198462">Actualizar Telefono</a></td>
                                                                                        </tr>
                                </tbody></table>
                        </td>
                </tr>
                <tr>
                        <th>Estado :
                        </th><td>
                                EMAIL_DELIVERY                                <br>
                                                        </td>
                </tr>	

                <tr>
                        <th>Cupon :
                        </th><td>987875815</td>
                        <th>Valor factura :
                        </th><td><b>$ 174350</b></td>
                </tr>	
        </tbody></table>
        </td>
    </tr>
    
</tbody></table>

<table class="table table-bordered table-condensed">
	<thead>
		<tr>
			<th>Courrier</th>
			<th>Corte</th>
			<th>Factura</th>
			<th>Producto</th>
			<th>Guia Courrier</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>BRAZE</td>
			<td>6-2020</td>
			<td>1477194471</td>
			<td></td>
			<td></td>
		</tr>
	</tbody>
</table>


<table class="table table-bordered table-condensed">
	<thead>
		<tr>
			<th colspan="3">Tiempos y Movimientos (TRAZABILIDAD)</th>
		</tr>
		<tr>
			<th>Estado</th>
			<th>Fecha de estado</th>
			<th>Fecha de Actualizacion</th>
		</tr>

	</thead>
	<tbody>

		<tr>
			<td>Fecha Orden</td>
			<td>2020-06-02 14:18:36.564294-05</td>
		</tr>
					    <tr>
        			<td>Fecha Transmision Base</td>
        			<td>2020-06-03 07:25:01.711719-05</td>
        			<td></td>
      			</tr><tr>
			              
		</tr><tr>
			<td>EMAIL_DELIVERY</td>
			<td>2020-05-23 00:00:00-05</td>
			<td></td>
		</tr>
                <tr>
			<td>Fecha Publicacion</td>
			<td></td>
                        <td></td>
		</tr>

	</tbody>
</table>

</div>
    """
    soup = BeautifulSoup(html, "html.parser")
    destinatario_table = soup.find('p', string='Destinatario').find_next_sibling('table')
    print(destinatario_table)
    print(destinatario_table.select_one('th:-soup-contains("Direccion") + td table tbody tr td').get_text(strip=True))