# Songling snark critical-subgraph audit

## Request and scope

Songling's 2026-05-05 follow-up asks us to verify that the edge-chromatic 3-critical subgraphs of each snark of order 18 or 20 are obtained by deleting a vertex, and to list all possible such subgraphs and how they are obtained.

This script audits the strict/common snark isomorphism classes already certified in `.hermes/reports/songling_followup_snark_deletion_audit.json`: the two order-18 classes and the six order-20 classes.  A graph is counted as edge-chromatic 3-critical only when both local edge-coloring implementations positively confirm `Δ`-criticality.

Important scope note: the script tests all pure one-vertex deletions and also the first non-induced strengthening, one vertex plus one additional edge deletion.  This is enough to find concrete counterexamples to the literal non-induced-subgraph reading.  It is not a brute-force enumeration of every smaller arbitrary edge subset of a snark.

## Top-level conclusion

Under the literal non-induced-subgraph reading, the proposed statement is **false** for the audited classes: there are edge-chromatic 3-critical subgraphs obtained by deleting one vertex and then one additional edge.

- Strict/common snark classes audited: `8`
- Pure vertex-deletion critical raw witnesses: `117`
- Vertex-plus-edge critical raw witnesses (not necessarily distinct isomorphism classes): `22`
- Snark classes with at least one vertex-plus-edge counterexample: `7`

If Songling intended **induced** subgraphs or specifically the previously studied order-17/order-19 residue graphs obtained as `S-v`, then the pure vertex-deletion lists below give the requested witnesses.  But the word `subgraph` should be qualified before promoting the statement to proof prose.

## Per-snark counts

### Order 18 strict/common class 1

- Source deletion-residue indices from prior audit: `[108, 149, 227, 326]`
- Completion graph6: `Q???C@?K?WPAI_S_?s?b?POA_G?`
- Pure vertex-deletion critical witnesses: `14`
- Vertex-plus-edge critical witnesses: `4`
- Critical-subgraph isomorphism classes found: `5`

Pure vertex-deletion witnesses:
- delete vertex `0` -> order-17 critical graph, census matches `[227]`, graph6 ``P???C@_E?`I_h?BOCWCS?OC?``
- delete vertex `1` -> order-17 critical graph, census matches `[149]`, graph6 ``P??C?@_EC`I_H?BOCW?S?oC?``
- delete vertex `2` -> order-17 critical graph, census matches `[108]`, graph6 ``P??CA?_EC`A_X?BOCWAS?_C?``
- delete vertex `4` -> order-17 critical graph, census matches `[108]`, graph6 `P??CA?oAC@C_T?BOAWAS?gC?`
- delete vertex `8` -> order-17 critical graph, census matches `[149]`, graph6 `P???C?oBCPDOS_@_AGAI?gC?`
- delete vertex `9` -> order-17 critical graph, census matches `[227]`, graph6 `P???C@?BCODOS_@gAKAI?gC?`
- delete vertex `10` -> order-17 critical graph, census matches `[227]`, graph6 `P???C@?KCOdOS_@gAKAI?g??`
- delete vertex `11` -> order-17 critical graph, census matches `[108]`, graph6 `P???C@?K?WDOS_@gAKAI?gA?`
- delete vertex `12` -> order-17 critical graph, census matches `[227]`, graph6 `P???C@?K?WPAS_@gAKAI?gA?`
- delete vertex `13` -> order-17 critical graph, census matches `[326]`, graph6 `P???C@?K?WPAI_@gAKAI?gA?`
- delete vertex `14` -> order-17 critical graph, census matches `[326]`, graph6 `P???C@?K?WPAI_S_AKAI?gA?`
- delete vertex `15` -> order-17 critical graph, census matches `[326]`, graph6 `P???C@?K?WPAI_S_?sAI?gA?`
- delete vertex `16` -> order-17 critical graph, census matches `[326]`, graph6 `P???C@?K?WPAI_S_?s?b?gA?`
- delete vertex `17` -> order-17 critical graph, census matches `[108]`, graph6 `P???C@?K?WPAI_S_?s?b?PO?`

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `3`, then edge `[5, 10]` -> order-17 critical graph, census matches `[196]`, graph6 ``P??CA?_CC`E_P?BO?WAS?gC?``
- delete vertex `5`, then edge `[3, 9]` -> order-17 critical graph, census matches `[196]`, graph6 `P??CA?_ACPD_T?@OAWAC?gC?`
- delete vertex `6`, then edge `[0, 7]` -> order-17 critical graph, census matches `[196]`, graph6 `P???A?oBCPD?S?@OAWAK?gC?`
- delete vertex `7`, then edge `[6, 12]` -> order-17 critical graph, census matches `[196]`, graph6 `P???A?oBCPD?S_@oAGAG?gC?`

### Order 18 strict/common class 2

- Source deletion-residue indices from prior audit: `[305, 324, 327, 329]`
- Completion graph6: `Q??CA?_CCOH_IODO?q?d?_K@_G?`
- Pure vertex-deletion critical witnesses: `12`
- Vertex-plus-edge critical witnesses: `6`
- Critical-subgraph isomorphism classes found: `6`

Pure vertex-deletion witnesses:
- delete vertex `1` -> order-17 critical graph, census matches `[324]`, graph6 `P?A?A?_c?oIOI_BGCgCB?OC?`
- delete vertex `3` -> order-17 critical graph, census matches `[329]`, graph6 `P?AA@??cAoEOA_BG?gCB?WC?`
- delete vertex `4` -> order-17 critical graph, census matches `[327]`, graph6 `P?AA@?O_AOCOE_BGAgCB?WC?`
- delete vertex `6` -> order-17 critical graph, census matches `[327]`, graph6 `P??A@?OaAWDOD_@GAGCB?WC?`
- delete vertex `7` -> order-17 critical graph, census matches `[329]`, graph6 `P??C@?OaAWD?D?@gAWCB?WC?`
- delete vertex `9` -> order-17 critical graph, census matches `[324]`, graph6 `P??CA?_aAWDGDO@_ASC@?WC?`
- delete vertex `11` -> order-17 critical graph, census matches `[329]`, graph6 `P??CA?_CCODGDO@cASC@_WA?`
- delete vertex `12` -> order-17 critical graph, census matches `[327]`, graph6 `P??CA?_CCOH_DO@cASC@_WA?`
- delete vertex `14` -> order-17 critical graph, census matches `[329]`, graph6 `P??CA?_CCOH_IODOASC@_WA?`
- delete vertex `15` -> order-17 critical graph, census matches `[327]`, graph6 `P??CA?_CCOH_IODO?qC@_WA?`
- delete vertex `16` -> order-17 critical graph, census matches `[305]`, graph6 `P??CA?_CCOH_IODO?q?d?WA?`
- delete vertex `17` -> order-17 critical graph, census matches `[305]`, graph6 `P??CA?_CCOH_IODO?q?d?_K?`

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `0`, then edge `[7, 13]` -> order-17 critical graph, census matches `[196]`, graph6 `P??CA?_CCoIOI?BGCg?B?oC?`
- delete vertex `2`, then edge `[5, 14]` -> order-17 critical graph, census matches `[196]`, graph6 `P?AA??_cAoAOI_@GCgCB?OC?`
- delete vertex `5`, then edge `[2, 8]` -> order-17 critical graph, census matches `[195]`, graph6 `P?AA??OaAODOC_@GAgCB?WC?`
- delete vertex `8`, then edge `[5, 11]` -> order-17 critical graph, census matches `[196]`, graph6 `P??CA?OaAODGDO@gAOC@?WC?`
- delete vertex `10`, then edge `[3, 13]` -> order-17 critical graph, census matches `[196]`, graph6 `P??CA?_CAWDG@O@cASC@_W??`
- delete vertex `13`, then edge `[0, 10]` -> order-17 critical graph, census matches `[195]`, graph6 `P??CA?_C?OH_IO@cASC@_WA?`

### Order 20 strict/common class 1

- Source deletion-residue indices from prior audit: `[793, 1682, 2000, 2001, 2002, 2003, 2020, 2021, 2054, 2214, 3032, 3119, 3129, 3229, 4643]`
- Completion graph6: ``S????A?O@_D?BAC`R?BA?@o?@oAH?CC_?``
- Pure vertex-deletion critical witnesses: `15`
- Vertex-plus-edge critical witnesses: `2`
- Critical-subgraph isomorphism classes found: `17`

Pure vertex-deletion witnesses:
- delete vertex `1` -> order-19 critical graph, census matches `[2054]`, graph6 `R???C??WA_BAHAk?GO?[??w?H?CH??`
- delete vertex `2` -> order-19 critical graph, census matches `[2003]`, graph6 `R???C@?G?_BAHAk?GO?[??w@H?CH??`
- delete vertex `3` -> order-19 critical graph, census matches `[2214]`, graph6 `R???C@?G@_BA@Ac?KO?[??w@H?CH??`
- delete vertex `4` -> order-19 critical graph, census matches `[4643]`, graph6 `R???C@?K@?@ADAc?KO?[??w@H?CH??`
- delete vertex `7` -> order-19 critical graph, census matches `[2021]`, graph6 `R???C@?K@O@aCae?K??K??W@D?CD??`
- delete vertex `8` -> order-19 critical graph, census matches `[3119]`, graph6 `R????@?K@O@aCae?KG?M??W@C?CD??`
- delete vertex `9` -> order-19 critical graph, census matches `[3032]`, graph6 `R????A?K@O@aCae?KG?M??W@C_CC??`
- delete vertex `10` -> order-19 critical graph, census matches `[3229]`, graph6 `R????A?O@O@_Cae?KG?M??[@C_CC_?`
- delete vertex `11` -> order-19 critical graph, census matches `[1682]`, graph6 ``R????A?O@_@`C_e?KG?M??[@C_CC_?``
- delete vertex `12` -> order-19 critical graph, census matches `[2000]`, graph6 ``R????A?O@_D?C`e?KG?M??[@C_CC_?``
- delete vertex `13` -> order-19 critical graph, census matches `[2001]`, graph6 `R????A?O@_D?BAe?KG?M??[@C_CC_?`
- delete vertex `14` -> order-19 critical graph, census matches `[2002]`, graph6 ``R????A?O@_D?BAC`KG?M??[@C_CC_?``
- delete vertex `17` -> order-19 critical graph, census matches `[3129]`, graph6 ``R????A?O@_D?BAC`R?BA?@o@C_CC_?``
- delete vertex `18` -> order-19 critical graph, census matches `[2020]`, graph6 ``R????A?O@_D?BAC`R?BA?@o?@oCC_?``
- delete vertex `19` -> order-19 critical graph, census matches `[793]`, graph6 ``R????A?O@_D?BAC`R?BA?@o?@oAH??``

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `0`, then edge `[2, 15]` -> order-19 critical graph, census matches `[3026]`, graph6 `R????A?WA_BAHAK?OO?[??wAH??H??`
- delete vertex `15`, then edge `[0, 14]` -> order-19 critical graph, census matches `[1917]`, graph6 ``R????A?O@_D?BAC`B??M??[@C_CC_?``

### Order 20 strict/common class 2

- Source deletion-residue indices from prior audit: `[1993, 3033, 3121, 3123, 3128, 3227, 4676, 4677, 4680, 4681, 4682, 4683, 4684]`
- Completion graph6: `S???C@?G?_P?p?Q_@g@GGCc??w?b?@CO?`
- Pure vertex-deletion critical witnesses: `13`
- Vertex-plus-edge critical witnesses: `3`
- Critical-subgraph isomorphism classes found: `16`

Pure vertex-deletion witnesses:
- delete vertex `0` -> order-19 critical graph, census matches `[3121]`, graph6 `R???C@?G?_P?d?E_H@@H??[?b?AG_?`
- delete vertex `3` -> order-19 critical graph, census matches `[4684]`, graph6 `R??CA?_?C_X?T?E_D@?H??[?B?@G_?`
- delete vertex `4` -> order-19 critical graph, census matches `[4681]`, graph6 `R??CA?_CC?X?P?A_D@?h??[?R?@G_?`
- delete vertex `5` -> order-19 critical graph, census matches `[3123]`, graph6 `R??CA?_CCOW?R?A_C@?h??[?R?@G_?`
- delete vertex `7` -> order-19 critical graph, census matches `[4682]`, graph6 ``R???A?_CCOW_Q_B?C`?d??[?P?@C_?``
- delete vertex `9` -> order-19 critical graph, census matches `[4676]`, graph6 ``R???C@?CCOW_Q_BOC`?c??K?P_@C_?``
- delete vertex `10` -> order-19 critical graph, census matches `[3227]`, graph6 ``R???C@?GCOW_Q_BOC`?c_?K?P_@C??``
- delete vertex `11` -> order-19 critical graph, census matches `[3128]`, graph6 `R???C@?G?_W_Q_BOC_?c_?M?P_@CO?`
- delete vertex `12` -> order-19 critical graph, census matches `[4680]`, graph6 `R???C@?G?_P?Q_BOC__c_?M?P_@CO?`
- delete vertex `14` -> order-19 critical graph, census matches `[3033]`, graph6 `R???C@?G?_P?p?Q_C__c_?M?P_@CO?`
- delete vertex `16` -> order-19 critical graph, census matches `[4677]`, graph6 `R???C@?G?_P?p?Q_@g@GG?M?P_@CO?`
- delete vertex `17` -> order-19 critical graph, census matches `[4683]`, graph6 `R???C@?G?_P?p?Q_@g@GGCc?P_@CO?`
- delete vertex `19` -> order-19 critical graph, census matches `[1993]`, graph6 `R???C@?G?_P?p?Q_@g@GGCc??w?b??`

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `2`, then edge `[7, 18]` -> order-19 critical graph, census matches `[1913]`, graph6 ``R??CA??GC_X?T?E_@@@H??[?`??G_?``
- delete vertex `15`, then edge `[3, 18]` -> order-19 critical graph, census matches `[3026]`, graph6 `R???C@?G?_P?p?Q_@g?c_?M?@_@CO?`
- delete vertex `18`, then edge `[2, 15]` -> order-19 critical graph, census matches `[1911]`, graph6 `R???C@?G?_P?p?Q_@g?GGCc??w@CO?`

### Order 20 strict/common class 3

- Source deletion-residue indices from prior audit: `[202, 203, 834, 1314, 1571, 2019, 2022, 3228]`
- Completion graph6: `S????A?O@?B_c_CWPG?L?Y??CW@C_AAO?`
- Pure vertex-deletion critical witnesses: `15`
- Vertex-plus-edge critical witnesses: `2`
- Critical-subgraph isomorphism classes found: `9`

Pure vertex-deletion witnesses:
- delete vertex `0` -> order-19 critical graph, census matches `[834]`, graph6 `R????A?O@oC_GoC_@gE_?AK@C_CC_?`
- delete vertex `1` -> order-19 critical graph, census matches `[1314]`, graph6 `R???C??O@oS_Goc_@gA_?AK@C_?C_?`
- delete vertex `2` -> order-19 critical graph, census matches `[1571]`, graph6 `R???C@??@oS_Goc_@gA_?AK?C_AC_?`
- delete vertex `3` -> order-19 critical graph, census matches `[2022]`, graph6 `R???C@?G?oO_?oc_@gB_?AK?c_AC_?`
- delete vertex `8` -> order-19 critical graph, census matches `[834]`, graph6 `R????@?G?wQOCOaO?oBO?@K?a_AA_?`
- delete vertex `9` -> order-19 critical graph, census matches `[1314]`, graph6 `R????A?G?wQOCWaO?sBO?@C?a?AA_?`
- delete vertex `10` -> order-19 critical graph, census matches `[1571]`, graph6 `R????A?O?wQOCWaO?sBO?@C?aOAA??`
- delete vertex `12` -> order-19 critical graph, census matches `[3228]`, graph6 `R????A?O@?B_CWaO?sBO?@E?aOAAO?`
- delete vertex `13` -> order-19 critical graph, census matches `[3228]`, graph6 `R????A?O@?B_c_aO?sBO?@E?aOAAO?`
- delete vertex `14` -> order-19 critical graph, census matches `[2019]`, graph6 `R????A?O@?B_c_CW?sBO?@E?aOAAO?`
- delete vertex `15` -> order-19 critical graph, census matches `[2019]`, graph6 `R????A?O@?B_c_CWPGBO?@E?aOAAO?`
- delete vertex `16` -> order-19 critical graph, census matches `[203]`, graph6 `R????A?O@?B_c_CWPG?L?@E?aOAAO?`
- delete vertex `17` -> order-19 critical graph, census matches `[203]`, graph6 `R????A?O@?B_c_CWPG?L?Y??aOAAO?`
- delete vertex `18` -> order-19 critical graph, census matches `[202]`, graph6 `R????A?O@?B_c_CWPG?L?Y??CWAAO?`
- delete vertex `19` -> order-19 critical graph, census matches `[202]`, graph6 `R????A?O@?B_c_CWPG?L?Y??CW@C_?`

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `6`, then edge `[7, 19]` -> order-19 critical graph, census matches `[3026]`, graph6 `R???C@?G?wQ?Coa_?gBO?@K?__A?_?`
- delete vertex `7`, then edge `[6, 18]` -> order-19 critical graph, census matches `[3026]`, graph6 `R???C@?G?wQOCOa??wBO?@K?__A?_?`

### Order 20 strict/common class 4

- Source deletion-residue indices from prior audit: `[3122, 4675, 4917, 5974, 5975]`
- Completion graph6: `S???C@?G?_@_o_WOT??B_DC?EG?PO?cG?`
- Pure vertex-deletion critical witnesses: `14`
- Vertex-plus-edge critical witnesses: `2`
- Critical-subgraph isomorphism classes found: `6`

Pure vertex-deletion witnesses:
- delete vertex `0` -> order-19 critical graph, census matches `[4675]`, graph6 `R???C@?G?oO_o_S??[@P?BC?PO@GO?`
- delete vertex `1` -> order-19 critical graph, census matches `[4675]`, graph6 `R??C?@?G?oO_O_s??[@P?BC?PO@GO?`
- delete vertex `2` -> order-19 critical graph, census matches `[4675]`, graph6 `R??CA??G?oW_O_c??[@P?BC?PO@GO?`
- delete vertex `3` -> order-19 critical graph, census matches `[3122]`, graph6 `R??CA?_??oW_W_k??[?P?BC?PO?GO?`
- delete vertex `5` -> order-19 critical graph, census matches `[3122]`, graph6 ``R??CA?_C?OW_W_i??[?`?@C?HO?gO?``
- delete vertex `6` -> order-19 critical graph, census matches `[5974]`, graph6 `R??CA?_C?WW?W_i??[?h?@C?HO?_O?`
- delete vertex `7` -> order-19 critical graph, census matches `[4917]`, graph6 `R???A?_C?WWOW?i??K?h?@c?HO?cO?`
- delete vertex `10` -> order-19 critical graph, census matches `[5975]`, graph6 `R???C@?G?WWOWOi??M?g_@_?G_?cO?`
- delete vertex `11` -> order-19 critical graph, census matches `[5975]`, graph6 `R???C@?G?_WOWOi??M?g_@a?Gg?c??`
- delete vertex `13` -> order-19 critical graph, census matches `[4917]`, graph6 `R???C@?G?_@_o_i??M?g_@a?Gg?cG?`
- delete vertex `15` -> order-19 critical graph, census matches `[4675]`, graph6 `R???C@?G?_@_o_WOT??g_@a?Gg?cG?`
- delete vertex `16` -> order-19 critical graph, census matches `[5974]`, graph6 `R???C@?G?_@_o_WOT??B_@a?Gg?cG?`
- delete vertex `17` -> order-19 critical graph, census matches `[3122]`, graph6 `R???C@?G?_@_o_WOT??B_DC?Gg?cG?`
- delete vertex `19` -> order-19 critical graph, census matches `[3122]`, graph6 `R???C@?G?_@_o_WOT??B_DC?EG?PO?`

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `9`, then edge `[6, 12]` -> order-19 critical graph, census matches `[1913]`, graph6 `R???C@?C?WW?WOi??K?g?@c?Go?cO?`
- delete vertex `12`, then edge `[9, 16]` -> order-19 critical graph, census matches `[1913]`, graph6 `R???C@?G?_@_WOi??M?g?@a?Gg?cG?`

### Order 20 strict/common class 5

- Source deletion-residue indices from prior audit: `[799, 800, 2025, 3127]`
- Completion graph6: ``S????A?O@_D?BAC`BG?M?p??AoB@?CA_?``
- Pure vertex-deletion critical witnesses: `14`
- Vertex-plus-edge critical witnesses: `3`
- Critical-subgraph isomorphism classes found: `6`

Pure vertex-deletion witnesses:
- delete vertex `0` -> order-19 critical graph, census matches `[3127]`, graph6 `R????A?WA_BAHAK_@oCO?@WB@??D??`
- delete vertex `1` -> order-19 critical graph, census matches `[2025]`, graph6 `R???C??WA_BAHAK_@oCO?@W@@?CD??`
- delete vertex `3` -> order-19 critical graph, census matches `[3127]`, graph6 ``R???C@?G@_BA@AC_@oEO?@W@`?CD??``
- delete vertex `4` -> order-19 critical graph, census matches `[3127]`, graph6 ``R???C@?K@?@ADAC_@oEO?@W@`?CD??``
- delete vertex `8` -> order-19 critical graph, census matches `[2025]`, graph6 `R????@?K@O@aCaEO?wEG??g@_?CB??`
- delete vertex `9` -> order-19 critical graph, census matches `[3127]`, graph6 `R????A?K@O@aCaEO?wEG??g@__CA??`
- delete vertex `10` -> order-19 critical graph, census matches `[2025]`, graph6 `R????A?O@O@_CaEO?wEG??k@__CA_?`
- delete vertex `11` -> order-19 critical graph, census matches `[2025]`, graph6 ``R????A?O@_@`C_EO?wEG??k@__CA_?``
- delete vertex `12` -> order-19 critical graph, census matches `[800]`, graph6 ``R????A?O@_D?C`EO?wEG??k@__CA_?``
- delete vertex `13` -> order-19 critical graph, census matches `[800]`, graph6 `R????A?O@_D?BAEO?wEG??k@__CA_?`
- delete vertex `14` -> order-19 critical graph, census matches `[799]`, graph6 ``R????A?O@_D?BAC`?wEG??k@__CA_?``
- delete vertex `16` -> order-19 critical graph, census matches `[800]`, graph6 ``R????A?O@_D?BAC`BG?M??k@__CA_?``
- delete vertex `17` -> order-19 critical graph, census matches `[800]`, graph6 ``R????A?O@_D?BAC`BG?M?p?@__CA_?``
- delete vertex `19` -> order-19 critical graph, census matches `[799]`, graph6 ``R????A?O@_D?BAC`BG?M?p??AoB@??``

Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):
- delete vertex `2`, then edge `[7, 19]` -> order-19 critical graph, census matches `[1917]`, graph6 `R???C@?G?_BAHAK_@oEO?@W@@?C@??`
- delete vertex `7`, then edge `[2, 18]` -> order-19 critical graph, census matches `[1910]`, graph6 `R???C@?K@O@aCaE??oEG??w@@?C@??`
- delete vertex `18`, then edge `[7, 14]` -> order-19 critical graph, census matches `[1917]`, graph6 ``R????A?O@_D?BAC`B??M?p??AoCA_?``

### Order 20 strict/common class 6

- Source deletion-residue indices from prior audit: `[1, 2, 191]`
- Completion graph6: `S??????oD?B?P_WOCc?i?Cg?Go?SOCAG?`
- Pure vertex-deletion critical witnesses: `20`
- Vertex-plus-edge critical witnesses: `0`
- Critical-subgraph isomorphism classes found: `3`

Pure vertex-deletion witnesses:
- delete vertex `0` -> order-19 critical graph, census matches `[191]`, graph6 `R????A?O@_P_o_QODO@I?CW?SO?CO?`
- delete vertex `1` -> order-19 critical graph, census matches `[2]`, graph6 `R????A?o@_@_O_QODO@I?CW?SOCCO?`
- delete vertex `2` -> order-19 critical graph, census matches `[2]`, graph6 `R????B?_@_H_O_AODO@I?CW?SOCCO?`
- delete vertex `3` -> order-19 critical graph, census matches `[1]`, graph6 `R????B?g?_H_W_IO@O?I?CW?SOCCO?`
- delete vertex `4` -> order-19 critical graph, census matches `[191]`, graph6 `R????B?g?_H_W_IOBO?i??W?COCCO?`
- delete vertex `5` -> order-19 critical graph, census matches `[191]`, graph6 `R????B?g?oG_W_GOAO?i?AW?KOCCO?`
- delete vertex `6` -> order-19 critical graph, census matches `[2]`, graph6 `R????B?g?oG_W_HOAo?a?AW?GOCCO?`
- delete vertex `7` -> order-19 critical graph, census matches `[1]`, graph6 `R????B?g?oGoW?HOA_?e?AW?IOC?O?`
- delete vertex `8` -> order-19 critical graph, census matches `[2]`, graph6 `R????B?g?oGoWOH?Ag?c?AG?IOCAO?`
- delete vertex `9` -> order-19 critical graph, census matches `[2]`, graph6 `R??????g?oGoWOHGAg?d?AG?IOCAO?`
- delete vertex `10` -> order-19 critical graph, census matches `[2]`, graph6 `R??????o?oGoWOHGAg?d?AK?I?CAO?`
- delete vertex `11` -> order-19 critical graph, census matches `[1]`, graph6 `R??????oD?GoWOHGAg?d?AK?IGCA??`
- delete vertex `12` -> order-19 critical graph, census matches `[2]`, graph6 `R??????oD?B?WOHGAg?d?AK?IGCAG?`
- delete vertex `13` -> order-19 critical graph, census matches `[191]`, graph6 `R??????oD?B?P_HGAg?d?AK?IGCAG?`
- delete vertex `14` -> order-19 critical graph, census matches `[2]`, graph6 `R??????oD?B?P_WOAg?d?AK?IGCAG?`
- delete vertex `15` -> order-19 critical graph, census matches `[1]`, graph6 `R??????oD?B?P_WOCc?d?AK?IGCAG?`
- delete vertex `16` -> order-19 critical graph, census matches `[191]`, graph6 `R??????oD?B?P_WOCc?i?AK?IGCAG?`
- delete vertex `17` -> order-19 critical graph, census matches `[2]`, graph6 `R??????oD?B?P_WOCc?i?Cg?IGCAG?`
- delete vertex `18` -> order-19 critical graph, census matches `[2]`, graph6 `R??????oD?B?P_WOCc?i?Cg?GoCAG?`
- delete vertex `19` -> order-19 critical graph, census matches `[1]`, graph6 `R??????oD?B?P_WOCc?i?Cg?Go?SO?`

## Conservative wording recommendation

Do not write that all edge-chromatic 3-critical subgraphs of these snarks are obtained by deleting a vertex unless `subgraph` is explicitly restricted (for example to the intended induced/vertex-deletion residue).  The audited data supports the safer statement: the listed pure vertex deletions are edge-chromatic 3-critical; however, under ordinary non-induced subgraph terminology, additional 3-critical subgraphs appear after deleting one more edge.
