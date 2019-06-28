# 1、在当前目录下执行：    
flask run   
来启动项目，默认端口为 http://127.0.0.1:5000/    
# 2、若要自定义启动端口，则执行如下命令：        
flask run --port=5001    
来启动项目，则启动端口为 http://127.0.0.1:5001/    
# 3、SQLite数据库使用SQLAlchemy框架来更新迁移    
## 1）命令：    
flask db init
flask db migrate
flask db upgrade    
## 2）sqlite数据库文件:     
./tmp/dev.db
## 3）sqlite数据库配置路径:    
工程根目录下 ".env" 文件中配置，配置方法参考：    
\#Unix/Mac - 4 initial slashes in total
engine = create_engine('sqlite:////absolute/path/to/foo.db')
\#Windows
engine = create_engine('sqlite:///C:\\path\\to\\foo.db')
\#Windows alternative using raw string
engine = create_engine(r'sqlite:///C:\path\to\foo.db')

### sqlite命令参考：
C:\Users\xl\Documents\http_server_tools\demo\flask_server_user\tmp>sqlite3    
SQLite version 3.22.0 2018-01-22 18:45:57    
Enter ".help" for usage hints.    
Connected to a transient in-memory database.    
Use ".open FILENAME" to reopen on a persistent database.    
sqlite> .open dev.db     \#打开数据库    
sqlite> .tables          \#查询数据库中所有数据表名称
alembic_version  roles            users       
sqlite> .schema    \#查询数据表结构
CREATE TABLE alembic_version (     
        version_num VARCHAR(32) NOT NULL,    
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)    
);    
CREATE TABLE users (    
        id INTEGER NOT NULL,    
        username VARCHAR(80) NOT NULL,    
        email VARCHAR(80) NOT NULL,    
        password BLOB,    
        created_at DATETIME NOT NULL,    
        first_name VARCHAR(30),    
        last_name VARCHAR(30),    
        active BOOLEAN,    
        is_admin BOOLEAN,    
        PRIMARY KEY (id),    
        UNIQUE (email),    
        UNIQUE (username),    
        CHECK (active IN (0, 1)),    
        CHECK (is_admin IN (0, 1))    
);    
CREATE TABLE roles (    
        id INTEGER NOT NULL,    
        name VARCHAR(80) NOT NULL,    
        user_id INTEGER,    
        PRIMARY KEY (id),    
        FOREIGN KEY(user_id) REFERENCES users (id),    
        UNIQUE (name)    
);     
sqlite> select * from users;    \#查询数据库表内容