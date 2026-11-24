using System;
using System.Collections.Generic;
using RogueElements;
using RogueEssence.Content;
using RogueEssence.Dungeon;

namespace RogueEssence.Menu
{
    internal sealed class DestinyHeadwearMenu : TitledStripMenu
    {
        public DestinyHeadwearMenu(Character member)
        {
            Label = "DESTINY_HEADWEAR_MENU";
            var rows = new (string Name, DestinyRibbon.Kind Style)[] {
                ("Cow-boy", DestinyRibbon.Kind.Cowboy), ("Casquette", DestinyRibbon.Kind.Cap),
                ("Haut-de-forme", DestinyRibbon.Kind.TopHat), ("Beret", DestinyRibbon.Kind.Beret),
                ("Bonnet", DestinyRibbon.Kind.Beanie), ("Lunettes de soleil", DestinyRibbon.Kind.Sunglasses)
            };
            var choices = new List<MenuTextChoice>();
            foreach (var row in rows)
            {
                var style = row.Style;
                choices.Add(new MenuTextChoice(row.Name, () => MenuManager.Instance.AddMenu(new DestinyRibbonMenu(member, style), true)));
            }
            int width = Math.Min(160, GraphicsManager.ScreenWidth - 16);
            int height = rows.Length * VERT_SPACE + GraphicsManager.MenuBG.TileHeight * 2 + TITLE_OFFSET;
            Initialize(new Loc((GraphicsManager.ScreenWidth - width) / 2, (GraphicsManager.ScreenHeight - height) / 2), width,
                "Accessoires", choices.ToArray(), 0);
        }
    }
}
