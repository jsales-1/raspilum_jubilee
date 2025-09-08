## Science Jubilee

<p align="justify">
Science Jubilee é uma plataforma de automação laboratorial de código aberto, baseada no sistema Jubilee, uma plataforma de movimento multiferramenta extensível, originalmente projetada como uma impressora 3D com troca automática de cabeças de ferramenta <a href="https://jubilee3d.com/index.php?title=Main_Page">[1]</a>.
</p>

<p align="center">
  <img src="./Imagens%20Readme/550px-Jubilee_v2.1.2.png" width="400"><br>
  <em>Figura 1 – Representação da estrutura da plataforma Jubilee 3D. </em>
</p>

<p align="justify">
A science-jubilee adapta essa infraestrutura para aplicações científicas, permitindo automação de experimentos com ferramentas como pipetas, câmeras, sondas e manuseio de amostras. A documentação oficial está disponível no site Science Jubilee Docs, que reúne guias de início rápido, construção da plataforma, desenvolvimento, referências da API e contribuições da comunidade. A plataforma é flexível e serve como base para diferentes aplicações de automação laboratorial, desde pipetagem e manipulação de amostras até aquisição de imagens. <a href="https://science-jubilee.readthedocs.io/en/latest/index.html">[2]</a>
</p>

### Experimentos da literatura que utilizaram a plataforma:

<p align="justify">
1. O artigo "A high-throughput workflow for the synthesis of CdSe nanocrystals using a sonochemical materials acceleration platform", publicado em 2023, apresenta uma plataforma aceleradora de materiais para síntese de nanocristais de CdSe. O sistema combinou o Jubilee com um equipamento de automação de líquidos da Opentrons OT-2, ultrassom e espectrometria, permitindo 625 condições experimentais <a href="https://pubs.rsc.org/en/content/articlehtml/2023/dd/d3dd00033h">[3]</a>.
</p>

<p align="center">
  <img src="./Imagens%20Readme/sonicator_article.jpg" width="500"><br>
  <em>Figura 2 – Plataforma de síntese de nanocristais com Jubilee 3D. </em>
</p>

<p align="justify">
2. O artigo "The Duckbot: A system for automated imaging and manipulation of duckweed" mostra um sistema para manipulação automatizada de lentilha d'água, uma planta que serve como modelo experimental. Foram implementadas ferramentas como pipeta, câmeras, loops de inoculação e módulos Python para controle via Jupyter notebooks, permitindo experimentos de crescimento com manipulação e análise automatizadas <a href="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296717">[4]</a>.
</p>

<p align="center">
  <img src="./Imagens%20Readme/Duckweed.png" width="500"><br>
  <em>Figura 3 – Sistema Duckbot para experimentos com lentilha d'água. </em>
</p>

## Jubilee RaspIlum

<p align="justify">
O Jubilee RaspIlum é uma plataforma multifuncional para automação de experimentos na Ilum.
</p>

<p align="center">
  <img src="./Imagens%20Readme/Raspilum.jpg" width="400"><br>
  <em>Figura 4 – Estrutura do Jubilee RaspIlum. </em>
</p>

### Estrutura

<p align="justify">
O sistema é constituído por perfis de alumínio anodizado, polias, correias, motores de passo, hastes metálicas, componentes impressos em PLA e outros componentes para conexão das peças. É possível conferir as etapas de montagem do sistema no manual oferecido no site do Jubilee 3D <a href="https://www.jubilee3d.com/index.php?title=Assembly_Instructions">[5]</a>. O Github do Science Jubilee também disponibiliza modelos 3D de ferramentas e componentes da estrutura do Jubilee.
</p>

### Componentes eletrônicos

<p align="justify">
A Jubilee RaspIlum se movimenta por meio de 5 motores de passo, sendo 2 para XY e 3 para Z. Há também um sexto motor para o trocador de ferramentas. Os motores são controlados através de uma Duet Mini e sua placa de extensão, as quais são tipicamente utilizadas para controle de máquinas CNC e impressoras 3D, recebendo G-Code e realizando as operações <a href="https://www.jubilee3d.com/index.php?title=Assembly_Instructions">[5]</a> <a href="https://docs.duet3d.com/Duet3D_hardware/Duet_3_family/Duet_3_Mini_5+_Hardware_Overview">[6]</a>. Com essas duas placas, temos 8 drivers para controle de motores de passo, havendo atualmente 6 ocupados. Diferentemente do planejado para impressoras 3D, não utilizamos sistema de aquecimento de superfície na Jubilee RaspIlum.
No esquemático a seguir, é possível conferir a conexão dos sensores de fim de curso e motores nos drivers e pinos I/O das placas Duet Mini com sua placa de extensão.
</p>

<p align="center">
  <img src="./Imagens%20Readme/duet3_mini_frame_wiring.png" width="400"><br>
  <em>Figura 5 – Esquemático de conexões da Duet Mini</em>
</p>



### Software

<p align="justify">
Para criar uma interface mais simplificada e acessível, uma placa Raspberry Pi 5 é utilizada como Single Board Computer, o que permite que o sistema seja controlado por um servidor local ou por linguagem Python. O Raspberry possui gravada uma imagem de sistema operacional Linux específica para o controle e comunicação com a placa Duet. A instalação foi feita seguindo o protocolo disponível no site da Duet 3D <a href="https://docs.duet3d.com/User_manual/Machine_configuration/SBC_setup">[7]</a>. Para utilizar o Python nesse subsistema Linux, foi necessário uma versão do Anaconda específica para Raspberry Pi, a qual foi instalada por meio do GitHub Miniforge <a href="https://github.com/conda-forge/miniforge">[8]</a>.
</p>

## Uso do Jubilee RaspIlum

### 1. Ligando o sistema

### 2. Controlando por Python

## Referências

<p align="justify">
[1] Jubilee 3D. Jubilee wiki. Disponível em: https://jubilee3d.com/index.php?title=Main_Page <br>
[2] Science Jubilee. Documentation. Disponível em: https://science-jubilee.readthedocs.io/en/latest/index.html <br>
[3] Telford J, Newton G, Shields R, Mohr S, Handley J, Thielbeer F, et al. A sonochemical materials acceleration platform for the synthesis of CdSe nanocrystals. Digital Discovery. 2023;2(3):856-865. <br>
[4] Babl L, Holten V, Reuter M, Schoof H. Duckbot: a modular open-source platform for automated experiments with duckweed. PLoS One. 2024;19(2):e0296717. <br>
[5] Jubilee 3D. Assembly Instructions. Disponível em: https://www.jubilee3d.com/index.php?title=Assembly_Instructions <br>
[6] DUET3D. Duet 3 Mini 5+ Hardware Overview. 2025. Disponível em: https://docs.duet3d.com/Duet3D_hardware/Duet_3_family/Duet_3_Mini_5%2B_Hardware_Overview <br>
[7] Duet 3D. SBC Setup. Disponível em: https://docs.duet3d.com/User_manual/Machine_configuration/SBC_setup <br>
[8] conda-forge/miniforge. Disponível em: https://github.com/conda-forge/miniforge
</p>
