using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using RogueEssence.Content;
using RogueEssence.Data;
using RogueEssence.Dungeon;
using RogueEssence.Ground;
using RogueElements;

namespace RogueEssence.Menu
{
    internal sealed class DestinyRibbonMenu : TitledStripMenu
    {
        private readonly Character member;
        private readonly DestinyRibbon.Kind style;
        private Dir8 direction = Dir8.Down;
        private readonly MenuText colorName;
        private readonly MenuText rotateHint;
        private readonly MenuText confirmHint;
        private readonly MenuText faceName;
        private readonly MenuText previewTitle;
        private static readonly string[] Directions = {
            "Face", "3/4 gauche", "Profil gauche", "Dos gauche", "Dos", "Dos droit", "Profil droit", "3/4 droit"
        };

        public DestinyRibbonMenu(Character member, DestinyRibbon.Kind style)
        {
            Label = "DESTINY_RIBBON_MENU";
            this.member = member;
            this.style = style;
            int width = Math.Min(240, GraphicsManager.ScreenWidth - 16);
            int rowCount = DestinyRibbon.Colors.Length;
            int height = rowCount * VERT_SPACE + GraphicsManager.MenuBG.TileHeight * 2 + TITLE_OFFSET;
            int saved = DestinyRibbon.IndexOf(member.DestinyRibbonColor);
            int confirmed = DestinyRibbon.StyleOf(member) == style || saved == 0 ? saved : -1;
            List<MenuTextChoice> options = new List<MenuTextChoice>();
            for (int ii = 0; ii < rowCount; ii++)
            {
                int choice = ii;
                options.Add(new MenuTextChoice(DestinyRibbon.Colors[ii].Name, () => Apply(choice), true,
                    ii == confirmed ? TextTan : Color.White));
            }
            Initialize(new Loc((GraphicsManager.ScreenWidth - width) / 2, (GraphicsManager.ScreenHeight - height) / 2),
                width, Title(style), options.ToArray(), saved);
            foreach (MenuTextChoice option in options)
            {
                Rect row = option.Bounds;
                option.Bounds = new Rect(row.X, row.Y, Math.Max(1, Math.Min(row.Width, width - 111 - row.X)), row.Height);
            }
            int previewX = width - 62;
            previewTitle = Small("Aperçu", previewX, 36, TextTan);
            colorName = Small("", previewX, 112, Color.White);
            faceName = Small("", previewX, 125, TextPale);
            rotateHint = Small("Gauche / droite", previewX, 142, Color.White);
            confirmHint = Small("Valider le choix", previewX, 154, TextTan);
        }

        private static string Title(DestinyRibbon.Kind style) => style switch {
            DestinyRibbon.Kind.Scarf => "Foulard de guilde", DestinyRibbon.Kind.Cowboy => "Chapeau cow-boy",
            DestinyRibbon.Kind.Cap => "Casquette", DestinyRibbon.Kind.TopHat => "Haut-de-forme",
            DestinyRibbon.Kind.Beret => "Beret", DestinyRibbon.Kind.Beanie => "Bonnet",
            DestinyRibbon.Kind.Sunglasses => "Lunettes de soleil", _ => "Ruban de guilde",
        };

        private static MenuText Small(string value, int x, int y, Color color)
            => new MenuText(value, new Loc(x, y), DirV.Up, DirH.None, color);

        private void Apply(int choice)
        {
            var save = DataManager.Instance.Save;
            if (GameManager.Instance.CurrentScene != GroundScene.Instance || DataManager.Instance.CurrentReplay != null
                || save == null || !save.ActiveTeam.Players.Contains(member) || !DestinyRibbon.TrySet(member, choice, style))
                return;
            SyncGroundActors(member);
            MenuManager.Instance.RemoveMenu();
        }

        // A ground save serializes the map and the team separately. After loading,
        // the visible actor may therefore contain a detached copy of the member.
        // Update only an unambiguously identified actor; never change an NPC or
        // replace its data, location, actions, inventory or script state.
        private static void SyncGroundActors(Character member)
        {
            var team = DataManager.Instance.Save.ActiveTeam;
            var map = ZoneManager.Instance.CurrentGround;
            if (map == null) return;
            foreach (GroundChar actor in map.IterateCharacters())
            {
                if (!(actor.Data is Character data)) continue;
                if (ReferenceEquals(data, member)) continue;
                Character match = null;
                if (ReferenceEquals(actor, map.ActiveChar))
                    match = team.Leader;
                else
                {
                    foreach (Character candidate in team.Players)
                    {
                        if (candidate.BaseForm != data.BaseForm || candidate.Nickname != data.Nickname ||
                            candidate.Discriminator != data.Discriminator || candidate.OriginalUUID != data.OriginalUUID ||
                            candidate.OriginalTeam != data.OriginalTeam || candidate.IsFounder != data.IsFounder ||
                            candidate.IsPartner != data.IsPartner) continue;
                        if (match != null) { match = null; break; }
                        match = candidate;
                    }
                }
                if (!ReferenceEquals(match, member) || data.BaseForm != member.BaseForm) continue;
                data.DestinyRibbonColor = member.DestinyRibbonColor;
                data.DestinyRibbonStyle = member.DestinyRibbonStyle;
                data.DestinyRibbonFitted = member.DestinyRibbonFitted;
            }
        }

        protected override void UpdateKeys(InputManager input)
        {
            // Gauche/droite ne change pas et n'applique jamais la couleur surlignée.
            if ((input.Direction == Dir8.Left || input.Direction == Dir8.Right) && input.Direction != input.PrevDirection)
                direction = (Dir8)(((int)direction + (input.Direction == Dir8.Left ? 1 : 7)) % 8);
            base.UpdateKeys(input);
        }

        public override void Draw(SpriteBatch batch)
        {
            base.Draw(batch);
            if (!Visible)
                return;
            Loc start = Bounds.Start;
            int x = Bounds.Right - 62;
            int y = Bounds.Y + 82;
            GraphicsManager.Pixel.Draw(batch, new Rectangle(x - 45, y - 28, 90, 54), null, new Color(23, 30, 47));
            GraphicsManager.Pixel.Draw(batch, new Rectangle(x - 45, y + 25, 90, 1), null, new Color(91, 104, 130));
            MonsterID id = member.BaseForm;
            CharSheet sheet = GraphicsManager.GetChara(id.ToCharID());
            Vector2 origin = new Vector2(x - sheet.TileWidth / 2, y - sheet.TileHeight / 2);
            sheet.DrawChar(batch, GraphicsManager.IdleAction, false, direction, origin,
                frames => CharSheet.TrueFrame(frames, (long)GraphicsManager.TotalFrameTick, false),
                Color.White, DestinyRibbon.ForPreview(id, CurrentChoice, style));
            colorName.SetText(DestinyRibbon.Colors[CurrentChoice].Name);
            faceName.SetText(Directions[(int)direction]);
            previewTitle.Draw(batch, start);
            colorName.Draw(batch, start);
            faceName.Draw(batch, start);
            rotateHint.Draw(batch, start);
            confirmHint.Draw(batch, start);
        }
    }
}
