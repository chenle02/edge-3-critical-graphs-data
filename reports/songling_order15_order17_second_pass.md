# Songling order-15/order-17 second-pass structural check

## Order 15

- direct triangle-inflation hits to order `13`: `76`
- triangle-rule violations: `6`
- Meredith total hits from order `11`: `12`
- overlap (triangle + Meredith): `8`
- Meredith-only residue: `4`
- remaining unexplained after triangle + Meredith: `14`

## Order 17

- direct triangle-inflation hits to order `15`: `639`
- triangle-rule violations: `44`
- Meredith total hits from order `13`: `112`
- overlap (triangle + Meredith): `77`
- Meredith-only residue: `35`
- Hajos `9+9` hits: `2` (survivor indices `195`, `196`)
- remaining unexplained after triangle + Meredith + Hajos: `98`

## Interpretation

- The order-15 first-pass union counts are confirmed.
- The order-17 first-pass direct triangle counts are confirmed.
- The earlier `35` figure for order-17 Meredith was the Meredith-only residue, not the full Meredith coverage. The full Meredith hit count is `112`.
- Hajos join is now detected as a genuine third mechanism at order `17`, but only for two survivors so far.
