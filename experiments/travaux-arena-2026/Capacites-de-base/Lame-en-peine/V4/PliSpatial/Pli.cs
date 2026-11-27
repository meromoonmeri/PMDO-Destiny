using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using RogueEssence.Dungeon;

namespace PliSpatial;
// Banc uniquement. Aucun fichier de jeu réel n'est modifié.
public static class Effet
{
    private sealed class Onde
    {
        public Character Target = null!;
        public int Frame, Duration;
        public DateTime Expire;
    }
    private static readonly List<Onde> Ondes = new();
    public static void Demarrer(Character cible, int duree)
    {
        if (cible == null) return;
        Ondes.Add(new Onde { Target = cible, Duration = Math.Clamp(duree, 1, 180), Expire = DateTime.UtcNow.AddSeconds(5) });
        Console.WriteLine("[PLI SPATIAL] démarrage " + cible.CharLoc);
    }
    public static void Nettoyer() => Ondes.Clear();

    // Appelé après le dessin ordinaire de gameScreen, pendant le même SpriteBatch.
    // Chaque micro-rectangle prélève la texture du rendu réel à un autre endroit.
    // Aucune image de biome, aucun quadrillage ou symbole n'est ajouté.
    public static void Dessiner(BaseDungeonScene scene, SpriteBatch batch, RenderTarget2D source, float drawScale)
    {
        for (int i = Ondes.Count-1; i >= 0; i--)
        {
            var o = Ondes[i];
            if (o.Frame >= o.Duration || DateTime.UtcNow > o.Expire) { Ondes.RemoveAt(i); continue; }
            float t = (float)o.Frame / o.Duration;
            float a = (float)Math.Pow(Math.Sin(Math.PI * t), 1.3);
            int cx=(int)((o.Target.CharLoc.X*24+12-scene.ViewRect.X)*drawScale);
            int cy=(int)((o.Target.CharLoc.Y*24+12-scene.ViewRect.Y)*drawScale);
            // Refracter le rendu réel en 12 facettes qui correspondent au quadrillage.
            // Enveloppe nulle aux extrémités : pas de coupure brusque en début ou fin.
            float strength=(float)Math.Pow(Math.Sin(Math.PI*t),1.2);
            int step=Math.Max(1,(int)Math.Round(drawScale));
            int rx=(int)(76*drawScale), ry=(int)(58*drawScale);
            float[] cutsU={.10f,.30f,.50f,.70f,.90f};
            float[] cutsV={.16f,.37f,.62f,.87f};
            for(int y=Math.Max(0,cy-ry);y<Math.Min(source.Height,cy+ry);y+=step)
            for(int x=Math.Max(0,cx-rx);x<Math.Min(source.Width,cx+rx);x+=step)
            {
                float lx=(x-cx)/drawScale+80, ly=(y-cy)/drawScale+80;
                float v=(ly-30.5f)/105.0f;
                if(v<cutsV[0] || v>=cutsV[3]) continue;
                float left=45-38*v, right=112+38*v;
                float u=(lx-left)/(right-left);
                if(u<cutsU[0] || u>=cutsU[4]) continue;
                int col=0,row=0;while(col<3 && u>=cutsU[col+1])col++;while(row<2 && v>=cutsV[row+1])row++;
                // Chaque morceau réfracte un point voisin différent du véritable décor.
                float edge=Math.Min(1,Math.Min(Math.Min((u-cutsU[0])*12,(cutsU[4]-u)*12),Math.Min((v-cutsV[0])*12,(cutsV[3]-v)*12)));
                float ox=(col-1.5f)*2.7f+(row-1)*1.1f;
                float oy=(row-1)*3.3f+(col-1.5f)*.55f;
                int dx=(int)Math.Round(drawScale*strength*edge*(ox+1.6*Math.Sin(t*13+row)));
                int dy=(int)Math.Round(drawScale*strength*edge*(oy+1.0*Math.Sin(t*11+col)));
                int wid=Math.Min(step,source.Width-x),hei=Math.Min(step,source.Height-y);
                int sx=Math.Clamp(x+dx,0,source.Width-wid),sy=Math.Clamp(y+dy,0,source.Height-hei);
                batch.Draw(source,new Rectangle(x,y,wid,hei),new Rectangle(sx,sy,wid,hei),Color.White);
            }
            o.Frame++;
        }
    }
}
