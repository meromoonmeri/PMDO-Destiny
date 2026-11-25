using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using RogueElements;
using RogueEssence.Data;
using RogueEssence.Dungeon;

namespace RogueEssence.Content
{
    /// <summary>Vêtements cosmétiques, indépendants de l'objet et du sprite de base.</summary>
    public static class DestinyRibbon
    {
        internal enum Kind { Ribbon, Scarf, Cowboy, Cap, TopHat, Beret, Beanie, Sunglasses }
        internal enum Fit
        {
            Upright, ShortNeck, FourLegs, Ruff, Bird, Wing, LongNeck, Flank,
            Shell, Metal, LowBody, Cloud, Apple, Gills, Kaiminus
        }

        internal readonly struct Wear
        {
            public readonly int Ink;
            public readonly Fit Cut;
            public readonly Kind Style;
            private readonly Loc[] seams;
            public Wear(int ink, Fit cut, Kind style = Kind.Ribbon, Loc[] seams = null)
            { Ink = ink; Cut = cut; Style = style; this.seams = seams; }
            public Loc Seam(Dir8 dir) => seams == null ? Loc.Zero : seams[(int)dir & 7];
        }

        internal sealed class Shade
        {
            public readonly string Key;
            public readonly string Name;
            public readonly Color[] Ink;
            public Shade(string key, string name, params int[] rgb)
            {
                Key = key;
                Name = name;
                Ink = Array.ConvertAll(rgb, c => new Color(c >> 16, (c >> 8) & 255, c & 255));
            }
        }

        // Liseré, pli, tissu, lumière ; rampe dessinée, pas un aplat teinté.
        internal static readonly Shade[] Colors = {
            new Shade(null, "Sans accessoire"),
            new Shade("garance", "Garance", 0x4A2033, 0xA43148, 0xDF5C65, 0xFFAE93),
            new Shade("ambre", "Ambre", 0x5C3327, 0xB76635, 0xE7A14A, 0xFFE3A0),
            new Shade("emeraude", "Émeraude", 0x203C37, 0x337C58, 0x63B67A, 0xC8E59B),
            new Shade("lagon", "Lagon", 0x213948, 0x27878C, 0x51C1BC, 0xB4F1E1),
            new Shade("saphir", "Saphir", 0x253052, 0x405BB2, 0x6B8DDC, 0xBFD8FF),
            new Shade("lilas", "Lilas", 0x45304E, 0x8558A3, 0xB487D6, 0xEBD9FA),
            new Shade("rose", "Rose nacré", 0x5A2D48, 0xAF557E, 0xE681A3, 0xFFCFD6),
            new Shade("ivoire", "Ivoire", 0x5B4842, 0xB59476, 0xF2DCAC, 0xFFF5D9),
            new Shade("encre", "Encre", 0x201A30, 0x4E4565, 0x746789, 0xC2ACCC),
        };

        private static readonly Dictionary<(string species, int form), (Fit cut, Loc[] seams)> Roster =
            new Dictionary<(string, int), (Fit, Loc[])>();
        internal static void ResetRoster() => Roster.Clear();

        public static void RegisterStarter(string species, int form, string cut, string seams)
        {
            if (String.IsNullOrEmpty(species) || form < 0) return;
            Roster[(species, form)] = (ReadFit(cut), ReadSeams(seams));
        }

        // Retouches relatives à la tête et au centre : cinq angles pour les
        // coupes symétriques, huit si le sprite porte un détail asymétrique.
        internal static Loc[] ReadSeams(string text)
        {
            if (String.IsNullOrEmpty(text)) return null;
            string[] rows = text.Split(';');
            if (rows.Length != 5 && rows.Length != 8) throw new FormatException("Couture Destiny : " + text);
            var result = new Loc[8];
            for (int d = 0; d < rows.Length; d++)
            {
                string[] pt = rows[d].Split(',');
                if (pt.Length != 2 || !Int32.TryParse(pt[0], out int x) || !Int32.TryParse(pt[1], out int y)
                    || x < -7 || x > 7 || y < -7 || y > 7)
                    throw new FormatException("Couture Destiny : " + text);
                result[d] = new Loc(x, y);
            }
            if (rows.Length == 5)
                for (int d = 5; d < 8; d++) result[d] = new Loc(-result[8-d].X, result[8-d].Y);
            return result;
        }

        internal static Fit ReadFit(string cut)
        {
            return cut switch
            {
                "cou_court" => Fit.ShortNeck,
                "quadrupede" => Fit.FourLegs,
                "criniere" => Fit.Ruff,
                "plumes" => Fit.Bird,
                "aile" => Fit.Wing,
                "long" => Fit.LongNeck,
                "flanc" => Fit.Flank,
                "carapace" => Fit.Shell,
                "coque_metal" => Fit.Metal,
                "tronc_bas" => Fit.LowBody,
                "nuage" => Fit.Cloud,
                "pomme" => Fit.Apple,
                "branchies" => Fit.Gills,
                "kaiminus" => Fit.Kaiminus,
                _ => Fit.Upright,
            };
        }

        internal static bool CanChoose(CharData member)
        {
            return Roster.Count > 0 && member != null && (DataManager.Instance?.Save is MainProgress)
                && (Roster.ContainsKey((member.BaseForm.Species, member.BaseForm.Form))
                    || member.DestinyRibbonFitted || (member.IsFounder && member.IsPartner));
        }

        internal static Kind StyleOf(CharData member) => member.DestinyRibbonStyle switch
        {
            "foulard" => Kind.Scarf, "cowboy" => Kind.Cowboy, "casquette" => Kind.Cap,
            "haut_de_forme" => Kind.TopHat, "beret" => Kind.Beret, "bonnet" => Kind.Beanie,
            "lunettes" => Kind.Sunglasses, _ => Kind.Ribbon,
        };
        internal static string StyleKey(Kind style) => style switch
        {
            Kind.Scarf => "foulard", Kind.Cowboy => "cowboy", Kind.Cap => "casquette",
            Kind.TopHat => "haut_de_forme", Kind.Beret => "beret", Kind.Beanie => "bonnet",
            Kind.Sunglasses => "lunettes", _ => null,
        };

        internal static bool TrySet(CharData member, int index, Kind style)
        {
            if (!CanChoose(member) || index < 0 || index >= Colors.Length)
                return false;
            member.DestinyRibbonColor = Colors[index].Key;
            // Un ruban déjà sauvegardé n'a pas de nouveau champ à migrer.
            member.DestinyRibbonStyle = index > 0 ? StyleKey(style) : null;
            member.DestinyRibbonFitted |= index > 0;
            return true;
        }

        internal static int IndexOf(string key)
        {
            if (String.IsNullOrEmpty(key)) return 0;
            for (int ii = 1; ii < Colors.Length; ii++)
                if (String.Equals(key, Colors[ii].Key, StringComparison.Ordinal)) return ii;
            return 0;
        }

        internal static Wear ForPreview(MonsterID visible, int ink, Kind style)
        {
            return Roster.TryGetValue((visible.Species, visible.Form), out var fit)
                ? new Wear(ink, fit.cut, style, fit.seams) : new Wear(ink, Fit.Upright, style);
        }
        internal static Wear From(CharData wearer, MonsterID visible)
        {
            if (wearer == null || String.IsNullOrEmpty(wearer.DestinyRibbonColor) || !CanChoose(wearer))
                return default;
            return ForPreview(visible, IndexOf(wearer.DestinyRibbonColor), StyleOf(wearer));
        }

        // Les deux passes ont le même espace que la tuile du sprite. Les pans
        // de profil sont sous le sprite (donc vraiment occultés, même en marche).
        internal readonly struct Run
        {
            public readonly int X;
            public readonly int Y;
            public readonly int Width;
            public readonly byte Ink;
            public Run(int x, int y, int width, byte ink) { X = x; Y = y; Width = width; Ink = ink; }
        }

        internal sealed class Pose
        {
            public readonly Loc Anchor;
            public readonly Run[] Behind;
            public readonly Run[] Front;
            public readonly bool Knot;
            public readonly bool Limited;
            public Pose(Loc anchor, Run[] behind, Run[] front, bool knot, bool limited)
            { Anchor = anchor; Behind = behind; Front = front; Knot = knot; Limited = limited; }
        }

        // Fittings share the palette, not a projection: each shape is sewn on one
        // stable place of the body before deciding which part the camera can see.
        private static readonly string[] FullBow = { "11...11", "143.341", "1234321", ".11211.", "..3.2..", ".31.21." };
        private static readonly string[] SmallBow = { "11.11", "13431", ".121.", ".3.2.", ".1.1." };
        private static readonly string[] PinBow = { "1.1", "343", "121", ".2." };
        private static readonly string[] TurnedBow = { "....11", ".1.341", "134321", ".1211.", "..23..", "...31." };
        private static readonly string[] SideFold = { ".11.", ".341", ".121", "..31" };

        private sealed class Forme
        {
            public readonly int Width, Height;
            private readonly byte[] alpha;
            private readonly int stride, start;
            private readonly bool flip;
            public int Left, Right, Top, Bottom;

            public Forme(byte[] alpha, int stride, int start, int w, int h, bool flip)
            {
                this.alpha = alpha; this.stride = stride; this.start = start; this.flip = flip;
                Width = w; Height = h; Left = w; Top = h; Right = Bottom = -1;
                for (int y = 0; y < h; y++)
                    for (int x = 0; x < w; x++)
                        if (Solid(x, y))
                        {
                            Left = Math.Min(Left, x); Right = Math.Max(Right, x);
                            Top = Math.Min(Top, y); Bottom = Math.Max(Bottom, y);
                        }
            }
            public bool Solid(int x, int y) => (uint)x < (uint)Width && (uint)y < (uint)Height
                && alpha[start + stride * y + (flip ? Width - 1 - x : x)] >= 64;

            public Loc Seat(int tx, int ty, bool guardHead)
            {
                tx = Math.Clamp(tx, Left, Right);
                ty = Math.Clamp(ty, Top, Bottom);
                int best = Int32.MaxValue;
                Loc seat = Loc.Zero;
                for (int y = Top; y <= Bottom; y++)
                    for (int x = Left; x <= Right; x++)
                    {
                        if (!Solid(x, y)) continue;
                        int dx = x - tx, dy = y - ty;
                        int score = 7 * dx * dx + (dy < 0 && guardHead ? 23 : 9) * dy * dy;
                        if (!Solid(x - 1, y)) score += 6;
                        if (!Solid(x + 1, y)) score += 6;
                        if (!Solid(x, y + 1)) score += 8;
                        if (score < best) { best = score; seat = new Loc(x, y); }
                    }
                return seat;
            }
        }

        private sealed class Textile
        {
            private const int Pad = 9;
            private readonly Forme sprite;
            private readonly int w, h;
            private readonly byte[] front, behind;
            public Textile(Forme sprite)
            {
                this.sprite = sprite;
                w = sprite.Width + Pad * 2; h = sprite.Height + Pad * 2;
                front = new byte[w * h]; behind = new byte[w * h];
            }
            public void Put(int x, int y, int color, bool back = false, bool bodyOnly = true)
            {
                if ((uint)(x + Pad) >= (uint)w || (uint)(y + Pad) >= (uint)h) return;
                if (!back && bodyOnly && !sprite.Solid(x, y)) return;
                (back ? behind : front)[x + Pad + (y + Pad) * w] = (byte)color;
            }
            public void Stamp(string[] pattern, int kx, int ky, Loc knot, bool mirror, bool bodyOnly)
            {
                int cols = pattern[0].Length;
                for (int y = 0; y < pattern.Length; y++)
                    for (int x = 0; x < cols; x++)
                    {
                        char pixel = pattern[y][x];
                        if (pixel == '.') continue;
                        int dx = (x - kx) * (mirror ? -1 : 1);
                        Put(knot.X + dx, knot.Y + y - ky, pixel - '0', bodyOnly: bodyOnly);
                    }
            }
            // Un pan ne doit pas ressembler à une île flottante. On retire
            // toute grappe de pixels extérieurs sans jonction au corps/tissu.
            private void TrimLoose()
            {
                bool[] joined = new bool[w * h];
                var queue = new Queue<int>();
                for (int yy = 0; yy < h; yy++)
                    for (int xx = 0; xx < w; xx++)
                    {
                        int n = yy * w + xx;
                        if (front[n] == 0 && behind[n] == 0) continue;
                        if (!sprite.Solid(xx - Pad, yy - Pad)) continue;
                        joined[n] = true; queue.Enqueue(n);
                    }
                while (queue.Count != 0)
                {
                    int old = queue.Dequeue(), x = old % w, y = old / w;
                    for (int dy = -1; dy <= 1; dy++)
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            if ((uint)(x + dx) >= (uint)w || (uint)(y + dy) >= (uint)h) continue;
                            int next = old + dy * w + dx;
                            if (joined[next] || (front[next] == 0 && behind[next] == 0)) continue;
                            joined[next] = true; queue.Enqueue(next);
                        }
                }
                for (int n = 0; n < joined.Length; n++)
                    if (!joined[n]) front[n] = behind[n] = 0;
            }
            private Run[] Pack(byte[] pixels)
            {
                var runs = new List<Run>();
                for (int y = 0; y < h; y++)
                    for (int x = 0; x < w; x++)
                    {
                        int n = y * w + x;
                        byte code = pixels[n];
                        if (code == 0) continue;
                        int end = x + 1;
                        while (end < w && pixels[y * w + end] == code) end++;
                        runs.Add(new Run(x - Pad, y - Pad, end - x, code));
                        x = end - 1;
                    }
                return runs.ToArray();
            }
            public Pose Finish(Loc anchor, bool knot, bool limited)
            {
                TrimLoose();
                return new Pose(anchor, Pack(behind), Pack(front), knot, limited);
            }
        }

        private static int Mix(int a, int b, int pct) => a + ((b - a) * pct) / 100;

        internal static Pose Place(byte[] alpha, int stride, int start, int w, int h, OffsetData anchor,
            bool flip, Dir8 dir, Fit cut, Kind style, Loc seam)
        {
            if (w < 1 || h < 1 || anchor == null) return null;
            var sprite = new Forme(alpha, stride, start, w, h, flip);
            if (sprite.Right < sprite.Left) return null;
            var center = flip ? anchor.CenterFlip : anchor.Center;
            var head = flip ? anchor.HeadFlip : anchor.Head;
            int cx = Math.Clamp(center.X + w / 2, sprite.Left, sprite.Right);
            int cy = Math.Clamp(center.Y + h / 2, sprite.Top, sprite.Bottom);
            int hx = Math.Clamp(head.X + w / 2, sprite.Left, sprite.Right);
            int hy = Math.Clamp(head.Y + h / 2, sprite.Top, sprite.Bottom);
            int sw = sprite.Right - sprite.Left + 1, sh = sprite.Bottom - sprite.Top + 1;
            int d = (int)dir & 7;
            int yaw = Math.Min(d, 8 - d);
            int forward = d == 0 || d == 4 ? 0 : d < 4 ? -1 : 1;
            bool front = yaw <= 1, back = yaw >= 3;
            bool sidePin = cut == Fit.Wing || cut == Fit.Flank;
            bool quadruped = cut == Fit.FourLegs || cut == Fit.Ruff;
            bool farSide = sidePin && d >= 1 && d <= 3;
            bool shielded = cut == Fit.Shell || cut == Fit.Metal;
            bool soft = cut == Fit.LowBody || cut == Fit.Cloud || cut == Fit.Apple;
            bool tiny = sw <= 14 || sh <= 14;
            bool compact = tiny || sidePin || shielded || soft || cut == Fit.Bird || cut == Fit.LongNeck || cut == Fit.Kaiminus;
            if (style != Kind.Ribbon && style != Kind.Scarf)
                return PlaceHead(sprite, hx, hy, yaw, forward, style, cut);
            int tx = Mix(cx, hx, yaw == 0 ? 45 : back ? 30 : 45);
            int ty = front ? Math.Max(cy - 1, hy + 2) : yaw == 2 ? Math.Clamp(cy, hy + 1, hy + 4) : Mix(cy, hy, 45) + 1;

            if (cut == Fit.ShortNeck || cut == Fit.Gills)
            {
                if (front) ty = Math.Max(cy, hy + 2) + (cut == Fit.Gills ? 1 : 0);
                tx = Mix(cx, hx, 30);
            }
            if (quadruped)
            {
                tx = Mix(cx, hx, yaw == 0 ? 45 : back ? 62 : 72);
                ty = yaw == 0 ? Math.Max(cy - 1, hy + 2) : back ? Mix(cy, hy, 68) + 1
                    : Math.Max(hy + 1, Mix(cy, hy, 72) + 1);
            }
            if (cut == Fit.Bird || cut == Fit.LongNeck)
            {
                tx = Mix(cx, hx, cut == Fit.LongNeck ? (yaw == 0 ? 55 : 70) : 42);
                ty = back ? Mix(cy, hy, 54) + 2 : Math.Max(hy + 2, Mix(cy, hy, 35));
            }
            if (sidePin)
            {
                // Épaule/aile droite anatomique, jamais l'aile opposée.
                int reach = Math.Clamp(sw / 4, 2, 5);
                int projectedRight = yaw == 0 ? -reach : yaw == 1 ? -reach / 2 : yaw == 2 ? 0 : yaw == 3 ? reach / 2 : reach;
                tx = Mix(cx, hx, cut == Fit.Wing ? 0 : 22) + projectedRight;
                ty = cut == Fit.Wing ? Math.Max(cy + 1, sprite.Top + sh * 64 / 100)
                    : (front ? cy + 1 : Mix(cy, hy, 20) + 1);
            }
            if (shielded)
            {
                // Encolure inexistante : attache sur la coque, côté corps,
                // jamais au point de tête (œil de Terhal, face de Frissonille).
                int away = Math.Clamp(cx - hx, -6, 6);
                tx = cx + (yaw > 0 && yaw < 4 ? away / 2 : 0);
                ty = cut == Fit.Metal ? (front ? Math.Min(cy, hy - 3) : cy - 1)
                    : front ? Math.Min(cy, hy - 2) : cy;
            }
            if (soft)
            {
                // Fruit et nuage : le bandeau prend la partie basse, sous les yeux
                // et sous les feuilles/pans du chapeau, et ne serre pas un faux cou.
                int ratio = cut == Fit.Apple ? 78 : cut == Fit.Cloud ? 74 : 69;
                tx = Mix(cx, hx, cut == Fit.Apple ? 5 : 22);
                ty = Math.Max(sprite.Top + sh * ratio / 100, cy + 1);
                if (!back) ty = Math.Max(ty, hy + 2);
            }
            int reserve = shielded || soft ? 1 : compact || quadruped ? 2 : 3;
            int bottom = Math.Max(sprite.Top, sprite.Bottom - reserve);
            ty = Math.Clamp(Math.Clamp(ty, sprite.Top, bottom) + seam.Y, sprite.Top, bottom);
            Loc seat = sprite.Seat(tx + seam.X, ty, front && !shielded);
            var piece = new Textile(sprite);

            // La bande suit la portion CONTINUE du corps au niveau de la couture.
            // La largeur de la tête/queue/ailes n'est pas celle de l'encolure.
            bool scarf = style == Kind.Scarf;
            int radius = sidePin ? Math.Clamp(sw / 6, 1, 3) : shielded ? Math.Clamp(sw / 4, 2, 5)
                : cut == Fit.LongNeck ? Math.Clamp(sh / 5, 2, 4) : soft ? Math.Clamp(sw * 2 / 5, 2, 5)
                : (quadruped || yaw == 2) ? Math.Clamp(sh / 4, 2, yaw == 2 ? 3 : 5)
                : Math.Clamp(sw * (scarf ? 38 : 31) / 100, 2, compact ? 4 : 6);
            if (farSide) radius = Math.Max(1, radius - 1);
            int neckStart = -radius, neckEnd = radius;
            if (quadruped && yaw == 2)
            {
                // Le museau ne fait pas partie de la circonférence du col.
                if (forward < 0) neckStart++; else neckEnd--;
            }
            int low = seat.X, high = seat.X;
            while (low > seat.X + neckStart && Covers(low - 1)) low--;
            while (high < seat.X + neckEnd && Covers(high + 1)) high++;
            for (int x = low; x <= high; x++)
            {
                int y = BandY(x);
                bool edge = x == low || x == high;
                piece.Put(x, y, edge ? 1 : back ? 2 : (scarf && (x - seat.X) * forward <= 0 ? 4 : 3));
                if (!farSide || scarf) piece.Put(x, y + 1, edge && !back ? 2 : 1);
                if (scarf && !compact && !quadruped && yaw != 2 && !edge && (back || x == seat.X))
                    piece.Put(x, y - 1, back ? 2 : 4);
            }

            int BandY(int x)
            {
                int rel = x - seat.X, towardFace = rel * forward;
                if (sidePin || soft || shielded) return seat.Y;
                if (forward == 0) return seat.Y - (Math.Abs(rel) >= radius && radius > 2 ? 1 : 0);
                int step = quadruped || cut == Fit.LongNeck ? 2 : 3;
                return seat.Y + (towardFace >= step ? 1 : towardFace <= -step ? -1 : 0);
            }
            bool Covers(int x) => sprite.Solid(x, BandY(x)) || sprite.Solid(x, BandY(x) + 1);
            piece.Put(seat.X, seat.Y, back ? 2 : 3);

            bool knot;
            if (!scarf)
            {
                // Ruban noué devant. À 90° on ne voit que son pli, et derrière
                // on ne copie surtout pas le nœud de face sur le dos.
                knot = !back && !farSide;
                if (knot)
                {
                    int lift = shielded ? 0 : 1;
                    int lead = sidePin || soft || shielded ? 0 : forward;
                    Loc at = sprite.Seat(seat.X + lead, seat.Y + lift, front && !shielded);
                    bool clip = compact || quadruped || yaw == 2;
                    if (yaw == 2) piece.Stamp(SideFold, 2, 1, at, forward < 0, clip);
                    else if (cut == Fit.Apple || cut == Fit.Cloud || cut == Fit.Wing) piece.Stamp(PinBow, 1, 1, at, false, true);
                    else if (compact || quadruped) piece.Stamp(SmallBow, 2, 1, at, forward > 0, clip);
                    else if (yaw == 1) piece.Stamp(TurnedBow, 3, 2, at, forward > 0, false);
                    else piece.Stamp(FullBow, 3, 2, at, false, false);
                }
            }
            else
            {
                // Foulard : bavette devant, lien de profil, nœud et pan courts
                // à la nuque (ou côté arrière du harnais). Pas de bavette dans le dos.
                knot = back && !farSide;
                if (front && !farSide)
                {
                    int bib = Math.Clamp(radius - 1, 1, compact ? 2 : 4);
                    int half = yaw == 1 ? Math.Max(bib - 1, 1) : bib;
                    int length = compact ? 3 : 4 + (radius >= 6 ? 1 : 0);
                    for (int yy = 0; yy < length; yy++)
                    {
                        int span = Math.Max(0, half - (yy + 1) / 2);
                        int x = seat.X + (yaw == 1 ? forward * (yy <= 1 ? 1 : 2) : 0);
                        for (int dx = -span; dx <= span; dx++)
                            piece.Put(x + dx, seat.Y + 1 + yy,
                                yy == length - 1 || (span > 0 && Math.Abs(dx) == span) ? 1 : yy <= 1 && dx < 0 ? 4 : yy > 2 ? 2 : 3);
                    }
                }
                if (yaw == 2 && !farSide)
                {
                    // La ligne du pan est tournée vers l'arrière du mouvement.
                    // Son début est sous le corps, sa sortie seulement peut être vue.
                    int rear = -forward;
                    int x0 = seat.X + rear * Math.Clamp((high - low) / 3, 1, 2);
                    int n = compact ? 4 : 7;
                    for (int j = 0; j < n; j++)
                    {
                        int x = x0 + rear * j;
                        int y = seat.Y + j / 2;
                        piece.Put(x, y - 1, 1, back: true);
                        piece.Put(x, y, j >= n - 2 ? 2 : 3, back: true);
                        if (j < n - 1) piece.Put(x, y + 1, 1, back: true);
                    }
                }
                if (knot)
                {
                    int rear = -forward;
                    Loc at = sprite.Seat(seat.X + rear * (compact ? 1 : 2), seat.Y, false);
                    // Le nœud de nuque est plus petit que le ruban décoratif.
                    piece.Put(at.X - 1, at.Y, 2); piece.Put(at.X, at.Y - 1, 1);
                    piece.Put(at.X, at.Y, 4); piece.Put(at.X + 1, at.Y, 2); piece.Put(at.X, at.Y + 1, 3);
                    int n = compact ? 3 : 5;
                    for (int j = 0; j < n; j++)
                    {
                        int x = at.X + (rear == 0 ? -1 : rear) * ((j + 1) / 2);
                        int y = at.Y + 1 + j;
                        piece.Put(x, y, j == n - 1 ? 1 : 3);
                        if (j < n - 1) piece.Put(x + (rear != 0 ? -rear : 1), y, 2);
                    }
                }
            }
            return piece.Finish(seat, knot, farSide);
        }

        // Accessoires de tête : point ancré sur la silhouette locale à proximité
        // du repère natif de tête, sans modifier la feuille du Pokémon.
        private static Pose PlaceHead(Forme sprite, int hx, int hy, int yaw, int forward, Kind style, Fit cut)
        {
            var textile = new Textile(sprite);
            int topY = Math.Clamp(hy, sprite.Top, sprite.Bottom);
            Loc nearHead = sprite.Seat(hx, topY, false);
            int topX = nearHead.X; topY = nearHead.Y;
            while (topY > sprite.Top && sprite.Solid(topX, topY - 1)) topY--;
            int headY = topY;
            while (headY < nearHead.Y)
            {
                int width = 0;
                for (int xx = topX - 3; xx <= topX + 3; xx++)
                    if (sprite.Solid(xx, headY)) width++;
                if (width >= 4) break;
                headY++;
            }
            if (style == Kind.Sunglasses)
            {
                // Le repère de tête natif peut être près du cou. Interpoler avec
                // le sommet de la masse crânienne, pas avec la pointe d'une oreille.
                int pct = cut == Fit.Metal ? 100 : cut == Fit.Shell ? 82 : cut == Fit.Bird ? 70 : 60;
                int ey = Mix(headY, nearHead.Y, pct);
                if (cut == Fit.Kaiminus) ey -= 2; // ses yeux sont au-dessus du museau
                Loc eye = sprite.Seat(hx, ey, false);
                // De dos, seuls les branches/bandeau sont visibles.
                if (yaw >= 3) {
                    textile.Put(eye.X - 2, eye.Y, 1); textile.Put(eye.X + 2, eye.Y, 1);
                } else if (yaw == 2) {
                    textile.Stamp(new[] { "1111", "1221", ".111" }, 2, 1, eye, forward > 0, true);
                } else {
                    textile.Stamp(new[] { "111.111", "1221221", ".11.11." }, 3, 1, eye, forward > 0, true);
                }
                return textile.Finish(eye, false, false);
            }
            // Recherche locale plutôt que sommet global : des oreilles ou ailes
            // éloignées ne doivent pas devenir le point de pose du chapeau.
            Loc top = sprite.Seat(topX, headY, false);
            string[] motif = style switch {
                Kind.Cowboy => new[] { "...11...11...", "..143111341..", "..133333331..", "..142222241..", "1113333333111", ".11111111111." },
                Kind.Cap => yaw >= 3 ? new[] { "..11111..", ".1433341.", "133333331", "112222211" }
                    : yaw == 2 ? new[] { "..11111..", ".1433341.", "133333331", "112222211", "...111111" }
                    : new[] { "..11111..", ".1433341.", "133333331", "112222211", ".1111111." },
                Kind.TopHat => new[] { "..11111..", "..14341..", "..13331..", "..13331..", "..12221..", ".1133311.", "111111111" },
                Kind.Beret => new[] { "...11....", ".111111..", "14333341.", "133333331", ".1122211." },
                _ => new[] { "...11....", "..1431...", ".143341..", "14333341.", "11222211." },
            };
            // Dernière rangée jointe à la tête ; le haut peut dépasser la tuile.
            int center = motif[0].Length / 2;
            bool mirror = style == Kind.Cap && yaw == 2 ? forward < 0 : forward > 0;
            textile.Stamp(motif, center, motif.Length - 1, top, mirror, false);
            return textile.Finish(top, false, false);
        }

        private static Texture2D dot;
        private static Texture2D Dot(GraphicsDevice device)
        {
            if (dot != null && !dot.IsDisposed && dot.GraphicsDevice == device) return dot;
            dot?.Dispose();
            dot = new Texture2D(device, 1, 1);
            dot.SetData(new[] { Color.White });
            return dot;
        }

        private static Color Tint(Color ink, Color tint) => new Color(
            ink.R * tint.R / 255, ink.G * tint.G / 255, ink.B * tint.B / 255, tint.A);

        private static Color[][] nightInks;
        private static Color[][] NightInks()
        {
            if (nightInks == null)
            {
                nightInks = new Color[Colors.Length][];
                for (int i = 0; i < Colors.Length; i++)
                    nightInks[i] = Array.ConvertAll(Colors[i].Ink, CharSheet.DestinyNightGrade);
            }
            return nightInks;
        }

        internal static void Draw(SpriteBatch batch, Vector2 frameTopLeft, Run[] runs, Color tint, Wear wear, bool night)
        {
            if (runs.Length == 0 || wear.Ink <= 0 || wear.Ink >= Colors.Length || tint.A == 0) return;
            Color[] colors = night ? NightInks()[wear.Ink] : Colors[wear.Ink].Ink;
            if (wear.Style == Kind.Sunglasses)
            {
                Color[] lenses = { Colors[wear.Ink].Ink[0], new Color(20, 24, 34), Colors[wear.Ink].Ink[2], new Color(175, 192, 204) };
                colors = night ? Array.ConvertAll(lenses, CharSheet.DestinyNightGrade) : lenses;
            }
            var brush = Dot(batch.GraphicsDevice);
            Color a = Tint(colors[0], tint), b = Tint(colors[1], tint), c = Tint(colors[2], tint), d = Tint(colors[3], tint);
            foreach (Run run in runs)
            {
                Color ink = run.Ink == 1 ? a : run.Ink == 2 ? b : run.Ink == 3 ? c : d;
                batch.Draw(brush, frameTopLeft + new Vector2(run.X, run.Y), null, ink, 0f,
                    Vector2.Zero, new Vector2(run.Width, 1), SpriteEffects.None, 0f);
            }
        }
    }
}
