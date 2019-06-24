关于npm    
1、使用之前记得安装淘宝镜像    
1）先将代理设置为空：    
$ npm config set proxy null    
2）使用淘宝镜像;    
$ npm install -g cnpm --registry=https://registry.npm.taobao.org    
    
注意需要使用淘宝淘宝定制的 cnpm 命令行代替默认的 npm：    
$ cnpm install [name]    
    