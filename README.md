## Science Jubilee

Science Jubilee é uma plataforma de automação laboratorial de código aberto, baseada no sistema Jubilee, uma plataforma de movimento multiferramenta extensível, originalmente projetada como uma impressora 3D com troca automática de cabeças de ferramenta [**[1]**](https://jubilee3d.com/index.php?title=Main_Page). 

![Jubilee](./Imagens%20Readme/550px-Jubilee_v2.1.2.png)

A science-jubilee adapta essa infraestrutura para aplicações científicas, permitindo automação de experimentos com ferramentas como pipetas, câmeras, sondas e manuseio de amostras. A documentação oficial está disponível no site Science Jubilee Docs, que reúne guias de início rápido, construção da plataforma, desenvolvimento, referências da API e contribuições da comunidade. A plataforma é flexível e serve como base para diferentes aplicações de automação laboratorial, desde pipetagem e manipulação de amostras até aquisição de imagens.  [**[2]**](https://science-jubilee.readthedocs.io/en/latest/index.html)

### Experiementos da literatura que utilizaram a plataforma:

1. O artigo "A high-throughput workflow for the synthesis of CdSe nanocrystals using a sonochemical materials acceleration platform", publicado em 2023, apresenta uma plataforma aceleradora de materiais para síntese de nanocristais de CdSe. O sistema combinou o Jubilee com um equipamento de automação de líquidos da Opentrons OT-2, ultrassom e espectrometria, permitindo 625 condições experimentais [**[3]**](https://pubs.rsc.org/en/content/articlehtml/2023/dd/d3dd00033h).  

2. O artigo "The Duckbot: A system for automated imaging and manipulation of duckweed" mostra um sistema para manipulação automatizada de lentilha d'água, uma planta quye serve. Foram implementadas ferramentas como, pipeta, câmeras, loops de inoculação e módulos Python para controle via Jupyter notebooks, permitindo experimentos de crescimento com manipulação e análise automatizadas [**[4]**](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296717).  

![Duckweed](./Imagens%20Readme/Duckweed.png)

## Jubilee RaspIlum

O Jubilee RaspIlum é uma plataforma multifuncional para automação de experimentos na Ilum. 

![Raspilum](./Imagens%20Readme/Raspilum.jpg)

### Estrutura
### Componenetes eletrônicos 
A Jubilee RaspIlum se movimenta por meio de 5 motores de passo, sendo 2 para XY e 3 para Z. Os motores são controlados através de placas Duet 3D, as quais são tipicamente utilizada para controle de máquinas CNC e impressoras 3D, recebendo G-Code e realizando as operações.  

Para criar um interface mais simplificada e acessível, uma placa Raspberry Pi 5 é utilizada como Single Board Computer, o que também permite que o sistema seja controlado por um servidor local ou por linguagem python. O Raspberry possui gravada uma imagem de sistema operacional linux específica para o controle e comunicação com a placa Duet. 


## Uso o Jubilee Raspilum

### 1. Ligando o sistema


### Controlando por python


## Referências

[1] Jubilee 3D. Jubilee wiki [Internet]. Disponível em: https://jubilee3d.com/index.php?title=Main_Page  
[2] Science Jubilee. Documentation [Internet]. Disponível em: https://science-jubilee.readthedocs.io/en/latest/index.html  
[3] Telford J, Newton G, Shields R, Mohr S, Handley J, Thielbeer F, et al. A sonochemical materials acceleration platform for the synthesis of CdSe nanocrystals. Digital Discovery. 2023;2(3):856-865.  
[4] Babl L, Holten V, Reuter M, Schoof H. Duckbot: a modular open-source platform for automated experiments with duckweed. PLoS One. 2024;19(2):e0296717.  


