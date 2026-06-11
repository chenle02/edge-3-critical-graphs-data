# Lemma E stress test: exhaustive hereditary failing tight-side hunt

Generated: 2026-06-10T08:11:26

## Question
A Lemma E counterexample needs a hereditarily failing tight side (the side
and ALL its qualifying tight sub-sides lack Delta-critical boundary-pair
completions, and the side passes the local embeddability conditions).
This run enumerates ALL tight-side shapes (degree sequence 3^{n-3} 2^3,
connected, no cyclic cut < 3) at the tested orders via geng — exhaustive,
unlike the random A13 probes (~3,400 sides/order).

## Summary
- Orders (exhaustive): [15, 17]
- Total candidates: 705359
- Failing sides (no critical completion): 192
- **Hereditarily failing sides (Lemma E seeds): 10**

## By order

| n | candidates | cyclic-cut<3 skip | not colorable | completes | failing | not embeddable | rescued by sub-side | HEREDITARY |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 50683 | 25917 | 73 | 24671 | 22 | 0 | 22 | 0 |
| 17 | 654676 | 303246 | 595 | 350665 | 170 | 0 | 160 | 10 |

## Failing sides detail

- order 15, `N???EA_E?wJ?GcH_?s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 15, `N???EA_EA_b_I_H_?s?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 15, `N???EA_EA_aoB_J?CS?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 15, `N???EA_E?gj?I_H_?s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_SD_CWB_BGB_?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_K?wBOQCPO?w?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_EAgBGHOP_@Q?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E@gI_ASB_KG?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E@gB_PCGo@S?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E?wJ?X?@oCI?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_EA_b_X?@oDG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_EA_ggL?B_DG?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E@_i_BOB_GW?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E@GaoT?QO@W?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E?gj?X?@oDG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CAA_E?ghGX?B_AW?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CA?oICgI__oQO?s?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CA?oICgIGP_BOPO?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CA?oICHM?aO@oIA?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CB@Oa?WSAH_DA@W?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 15, `N??CB@OI?gSAQ_BOOo?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 15, `N?AA@?OaBCHGCWD_DC?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P????A?WAoI_B_aOSO?F?DC?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P????A?W?wBOT?`OSO?F?QC?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oB_U?@aCg@E??s?`: embeddable=True, sub-sides=6, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oAoF?R?CH@E??s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oAoF?PADG@E??s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oAoD_POHG@OO?w?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?o?wD_P_HG@OOCW?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?o?wD_POBG@OOOg?`: embeddable=True, sub-sides=6, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oI@L?J??w?U??s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oI@R?L??w?U??w?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oI@F?B_Cg@E??s?`: embeddable=True, sub-sides=7, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oG`F?L?CW?U??s?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oA`E_R?Cg@E??s?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?oA`E_Q_CW@I?@S?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?o?pF?T?DG@E??s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?g?o?pDOF?L?AE?_S?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P????B?K?WCSw?aOBGAK?CQ?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?GCoI_M?Oo@Q?L?gC?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?gA_U?GWBO@Q?[?D_?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?gA_D_J?AoQO?F?@K?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?gA_D_J?Cc@W?L?_W?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g@_X?EOAW?sAK?D_?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g@_B_EOQAGo?L??w?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g@_B_EOQAGS?L?@o?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g@_@oF?R??T?e?OW?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI_DGB_DO?EOWG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_U?W_?s?F?@Q?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_U?H_?s?EOWG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_U?OgCc?M?Ga?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_U?@aKO?F?HG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_T?AgKO?F?@Q?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_T?@gCSAE?IA?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_S_@gCo?QOWG?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oB_E_PAKO?F?HG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoM?QGGo?M?GI?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoT?R?D@?F??w?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoL?B_H@@B??s?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoL?AQH_AD?Gg?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoF?R?KO?F?GI?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoF?PAKO?F?IG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoF?PADO@B??s?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oAoD_WAHC?J?I_?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oGcU?D_Co?F?IA?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oGcT?K_@o?F?AQ?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oGcT?B_CP?U?CW?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oGcT?AaEO?M?IG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oGcT?AaEO?F?J??`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI@Y?B_?s?M?KG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI@Y?AW?s?k?H_?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI@F?H_?s?U?WG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI@F?B_KO?F?HG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI@KGAW@oAK?H_?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oI@PGE_CS?M?J??`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oE@D_B_H_AB??w?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oE@D_BOH_AD??w?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oG`H_@gBO?q?WG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oC`F?T?@W?F?_g?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oC`F?DOGW?T?_K?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oC`DOT?HO?T??w?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oC`DOT?GS?T?Ao?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`U?B_KO?F?HG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`U?@gCSAE?J??`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`M?Q_?s?M?OW?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`S_W_?[?X?J??`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`K_AoHOAH?@W?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`E_R?KO?F?HG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`E_PGKO?M?AW?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`B_R?KO?F?KG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?oA`B_I_IO@B?@S?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?o?pF?T?KO?F?IG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?g?o?pF?L?GQ@B?aG?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OW_POcO@o?T??i?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OOocOBOI_AD?Ag?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OAod?oOGS?T?@S?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OAocOb?GgAD?Ag?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OWGs?@W@S?[?@a?`: embeddable=True, sub-sides=6, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OOgp?D_ASAP??s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OOgc_S_?kAP?@c?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OOgoGSO@S?[?@a?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K@OOas?DO@o?T?Oa?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K@OOae?DOKO?F?Oa?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K@OOae?DOKO?F??i?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K@OOae?DOGP@D?QO?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K@OOae?DOGP?L?Y??`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K@OOaHOOoHC?d?E_?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?WDOK__cG`?R?DG?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?WDAe?S_Gg?L?gA?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?WDAb?P_IG?d?gA?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?WOQi?GoGg?h?SA?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K?WOQg_W_BG?J?QA?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?WOQg_I_IG?J?QA?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?WOQK_W_HC?J?F??`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?W@QK_g_I_?J?OQ?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?W@QK_g_I_?J?_I?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?W@QK_H_W_?b?OQ?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@?K?W@Qa_WACc?e?p??`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???C@?K?W@QI_c_K_?J?OQ?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P???CB?W?o?oDAJ?DO?EGSC?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S@_@_oGI_@o?EG@E?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCOC_SGI_Ao?E_@P?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCOC_SGD_@O_M?GS?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCOC_SG@`BO@E?@S?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO@_gAB_A_`E??w?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO@_`AJ?AO_e??s?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO@_`AI@Ao?e??s?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO@_BAH_CWCa??h?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO?o[?J??q?b?A`?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO?o@gL?L??a_A`?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO?ogAJ??w?cGAW?`: embeddable=True, sub-sides=5, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO?ogAJ??W_k?AW?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO?ogAB@B_@E??w?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_SCO?o`AG`@W?w?CS?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S@OA_oGAaOW@K?BO?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S@OA_oGAa@WCK?HO?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S@O?ooC@PAoCS?EO?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S@O?ocCPOOo?q?A`?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S@O?oD@d?GW?S_aO?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S?W@O[?h??i?d?_Q?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S?W@O[?DGOO`E?AS?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P???C@_S?W@OoG`OE_@E?Cc?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOX?J?S_?Y?HOKO?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P??CA?_CCOX?IGL?AW?K_OI?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOX?IGKOAo?H_Oa?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOW_H_B_BC?B_KO?`: embeddable=True, sub-sides=0, some sub-side completes=False, HEREDITARY=True
- order 17, `P??CA?_CCOK_SO?[@c@K?Cc?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOK_HOSOBC?D_BC?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOK_OWJ?Ac?S_?q?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOK_OWKOB_?K_AK?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOK_OWKGB_?K_AS?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOP_Q_GaAg?H_KG?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOH_X?@oEG?`_AK?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOH_X?DGAI?E_IG?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOH_WO@WE_?S_?i?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOWOI_F?AK?I_WA?`: embeddable=True, sub-sides=1, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKG[?F??e?K_?w?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKG[?DC@E?L?BO?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKGX?DOBC?D_BC?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKGSGHCB_?K_?w?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKGQGDGAa?M?IC?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKGQGDGAa?E_J??`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOKGSCDGD_?L??s?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOHGX?KG?i?c_BG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOGgX?L?BC?D_AS?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOGgWGM?Aa?E_@g?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOGgWGKOB_?K_AK?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_CCOGgWGKCB_?L??s?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOC_aC@Q@KAc?D_?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_R?IA?K_M?Gg?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_g_IC?c_i?Ag?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_K_@g@_`B?_S?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_gCDG@S@E?@P?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_gC@g@o?aGIG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_gCB@?s?e?GW?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_gC@H@o?e?GW?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_aCD_CO_R?@Q?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_aCKGCo?F?@P?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_aCH@CS?M?CW?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_aC?pEO@H?BG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_ECHGCoCB??p?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_`CE_CO_R?@Q?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_cAOA_PAB_D?`B??w?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_c?o@_p?@SKG@D??h?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_c?o@_o_W_AK?I_HG?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_c?o@_B_PAK?`B??w?`: embeddable=True, sub-sides=4, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_c?o@_oCK_CKAI??i?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_c?o@_oCWOAS@H??q?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?_c?cH?g_@KD_?J?CQ?`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?__a_@_e?I_?c_I_KG?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?__a_@_e?B_CA_b?@Q?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 17, `P??CA?___oA_q?IGCWAI?@K?`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False

## Guardrails
- Finite exhaustive local evidence; not an all-order theorem.
- A hereditarily failing side is only a counterexample SEED; refuting
  Lemma E additionally requires an ambient critical embedding.
- Do not send Songling-facing prose from this audit without a fresh gate.

JSON sibling: `lemma_e_stress_test_hereditary_failing_sides_20260610_081126.json`
