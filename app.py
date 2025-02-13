from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory
import os



#estamos creando nuestra aplicacion y estamos asociando y renderizando nuestro template
#con el archivo html

#instancia de la clase flask
app = Flask(__name__)

#configurar las sesiones

app.secret_key="develoteca"

#estamos creando la conexion a la base de datos
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)



#acceder a la imagen

@app.route('/img/<imagen>')

def imagenes(imagen):    
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

#llamar css de bootsrap

@app.route("/css/<archivocss>")

def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'), archivocss)

# conexion sitio

@app.route('/')

def inicio():
    return render_template('sitio/index.html')

@app.route('/libros')

def libros():
    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    
    return render_template('sitio/libros.html', libros=libros)

@app.route('/nosotros')

def nosotros():
    return render_template('sitio/nosotros.html')

# conexion admin *******************************************

@app.route('/admin/')

def admin_index():
    
    if not 'login' in session:
        return redirect('/admin/login')
    return render_template('admin/index.html')

@app.route('/admin/login')

def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])

def admin_login_post():
    _usuario=request.form['txtUsuario'] 
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)
    
    if _usuario=="admin" and _password=="123":
        session["login"]=True
        session["usuario"]= "Administrador"        
        return redirect("/admin")
    
    return render_template("admin/login.html", mensaje="Acceso denegado")

@app.route('/admin/cerrar')

def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login') 

@app.route('/admin/libros')

def admin_libros():
    #consultar los datos
    
    if not 'login' in session:
        return redirect('/admin/login')

    
    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)
    
    return render_template('admin/libros.html',libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])

def admin_libros_guardar():
    
    if not 'login' in session:
        return redirect('/admin/login')
    
    _nombre= request.form['txtNombre']
    _url= request.form['txtURL']
    _archivo= request.files['txtImagen']
    
    #adjuntar archivo al servidor
    
    tiempo=datetime.now()
    horaactual=tiempo.strftime('%Y%H%M%S')
    
    if _archivo.filename !="":
        nuevoNombre=horaactual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+ nuevoNombre)  
    
    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL,%s,%s ,%s);"
    datos=(_nombre,nuevoNombre,_url)
    
    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    
    
    
    print(_nombre)
    print(_url)
    print(_archivo)
    return redirect('/admin/libros')



@app.route('/admin/libros/borrar', methods={'POST'} )

def admin_libros_borrar():
    
    if not 'login' in session:
        return redirect('/admin/login')

    _id=request.form['txtID']
    print(_id)
    #consulta del registro selccionado
    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s", (_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libros)
    
    
    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))
    
    #borrado del registro seleccionado
    conexion = mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM `libros` WHERE id=%s", (_id))
    conexion.commit()
    
    
    return redirect('/admin/libros')


if __name__== '__main__':
    app.run(debug=True)