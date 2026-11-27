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
            int rx=Math.Max(8,(int)(45*drawScale)), ry=Math.Max(8,(int)(38*drawScale));
            int step=Math.Max(1,(int)Math.Round(drawScale));
            for (int y=Math.Max(0,cy-ry);y<Math.Min(source.Height,cy+ry);y+=step)
            for (int x=Math.Max(0,cx-rx);x<Math.Min(source.Width,cx+rx);x+=step)
            {
                float nx=(x-cx)/(float)rx, ny=(y-cy)/(float)ry;
                float q=1-nx*nx-ny*ny;
                if (q<=0) continue;
                float f=q*q*a;
                int dx=(int)Math.Round(f*(8*nx*Math.Cos(t*18)+6*Math.Sin(ny*5.5+t*24))*drawScale);
                int dy=(int)Math.Round(f*(6*ny*Math.Sin(t*20)+3.5*Math.Sin(nx*5.2-t*18))*drawScale);
                int wid=Math.Min(step,source.Width-x), hei=Math.Min(step,source.Height-y);
                int sx=Math.Clamp(x+dx,0,source.Width-wid), sy=Math.Clamp(y+dy,0,source.Height-hei);
                batch.Draw(source, new Rectangle(x,y,wid,hei), new Rectangle(sx,sy,wid,hei), Color.White);
            }
            o.Frame++;
        }
    }
}
