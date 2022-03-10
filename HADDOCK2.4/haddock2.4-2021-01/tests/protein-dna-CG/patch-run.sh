#!/bin/bash
cat run.cns |\
   sed "s/{===>} dna_mol3=false;/{===>} dna_mol3=true;/g" |\
   sed "s/{===>} prot_top_mol3=\"protein-allhdg5-4.top\";/{===>} prot_top_mol3=\"dna-rna-allatom-hj-opls-1.3.top\";/g" |\
   sed "s/{===>} prot_link_mol3=\"protein-allhdg5-4-noter.link\";/{===>} prot_link_mol3=\"dna-rna-1.3.link\";/g" |\
   sed "s/{===>} prot_par_mol3=\"protein-allhdg5-4.param\";/{===>} prot_par_mol3=\"dna-rna-allatom-hj-opls-1.3.param\";/g" |\
   sed "s/{===>} prot_cg_top_mol3=\"protein-CG-Martini-2-2.top\";/{===>} prot_cg_top_mol3=\"dna-CG-MARTINI-2-1p.top\";/g" |\
   sed "s/{===>} prot_cg_link_mol3=\"protein-CG-Martini-2-2.link\";/{===>} prot_cg_link_mol3=\"dna-CG-MARTINI-2-1p.link\";/g" |\
   sed "s/{===>} prot_cg_par_mol3=\"protein-CG-Martini-2-2.param\";/{===>} prot_cg_par_mol3=\"dna-CG-MARTINI-2-1p.param\";/g" |\
   sed 's/{===>} w_desolv_0=1.0/{===>} w_desolv_0=0.0/g' |\
   sed 's/{===>} w_desolv_1=1.0/{===>} w_desolv_1=0.0/g' |\
   sed 's/{===>} w_desolv_2=1.0/{===>} w_desolv_2=0.0/g' |\
   sed 's/{===>} epsilon_0=10.0/{===>} epsilon_0=78.0/g' |\
   sed 's/{===>} epsilon_1=1.0/{===>} epsilon_1=78.0/g' |\
   sed 's/{===>} epsilon_1=10.0/{===>} epsilon_1=78.0/g' |\
   sed 's/{===>} dielec_0=rdie/{===>} dielec_0=cdie/g' |\
   sed 's/{===>} dielec_1=rdie/{===>} dielec_1=cdie/g' |\
   sed "s/{===>} dnarest_on=false/{===>} dnarest_on=true/g" |\
   sed "s/{===>} dnacgrest_on=false/{===>} dnacgrest_on=true/g" |\
   sed "s/{===>} structures_0=1000/{===>} structures_0=2/g" |\
   sed "s/{===>} structures_1=200/{===>} structures_1=2/g" |\
   sed "s/{===>} waterrefine=200/{===>} waterrefine=2/g" >run.cns.new
\mv run.cns.new run.cns
