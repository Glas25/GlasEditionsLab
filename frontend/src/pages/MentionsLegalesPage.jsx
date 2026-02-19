import { Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function MentionsLegalesPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-6 md:px-12">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-serif text-xl font-semibold tracking-tight">GlasEditionsLab</span>
            </Link>
            <Link to="/">
              <Button variant="ghost" className="rounded-sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 md:px-12 py-12">
        <h1 className="font-serif text-4xl font-bold mb-8">Mentions Légales</h1>
        
        <div className="prose prose-stone max-w-none space-y-8">
          <p className="text-muted-foreground">Dernière mise à jour : Février 2026</p>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">1. Éditeur du site</h2>
            <p>Le site GlasEditionsLab accessible à l'adresse <strong>glaseditionslab.com</strong> est édité par :</p>
            <div className="bg-stone-50 p-6 rounded-sm mt-4">
              <ul className="list-none space-y-2 m-0 p-0">
                <li><strong>Raison sociale :</strong> EI Glas25 (Entreprise Individuelle)</li>
                <li><strong>Propriétaire :</strong> M. Prencipe Alexandre</li>
                <li><strong>Siège social :</strong> 1 Ter rue du Cotay, 25300 Arçon, France</li>
                <li><strong>SIRET :</strong> 520 388 166 00024</li>
                <li><strong>Numéro de TVA intracommunautaire :</strong> Non assujetti (Article 293 B du CGI)</li>
                <li><strong>Email :</strong> <a href="mailto:glaseditionslab@gmail.com" className="text-primary hover:underline">glaseditionslab@gmail.com</a></li>
                <li><strong>Directeur de la publication :</strong> M. Prencipe Alexandre</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">2. Hébergement</h2>
            <p>Le site GlasEditionsLab est hébergé par :</p>
            <div className="bg-stone-50 p-6 rounded-sm mt-4">
              <ul className="list-none space-y-2 m-0 p-0">
                <li><strong>Hébergeur :</strong> Emergent Labs</li>
                <li><strong>Site web :</strong> <a href="https://emergentagent.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">emergentagent.com</a></li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">3. Activité</h2>
            <p>
              GlasEditionsLab est une plateforme en ligne de génération automatique de livres 
              (fiction et non-fiction) utilisant l'intelligence artificielle. Le service permet 
              aux utilisateurs de créer des ouvrages complets à partir d'une idée initiale, 
              incluant la génération de plans, de chapitres et de couvertures.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">4. Propriété intellectuelle</h2>
            <p>
              L'ensemble des éléments constituant le site GlasEditionsLab (textes, graphismes, 
              logiciels, images, photographies, sons, plans, noms, logos, marques, créations et 
              œuvres protégeables diverses, bases de données, etc.) ainsi que le site lui-même, 
              relèvent des législations françaises et internationales sur le droit d'auteur et 
              la propriété intellectuelle.
            </p>
            <p className="mt-4">
              Ces éléments sont la propriété exclusive de EI Glas25. Toute reproduction, 
              représentation, modification, publication, transmission, dénaturation, totale ou 
              partielle du site ou de son contenu, par quelque procédé que ce soit, et sur 
              quelque support que ce soit est interdite sans l'autorisation écrite préalable 
              de EI Glas25.
            </p>
            <p className="mt-4">
              <strong>Concernant les contenus générés par les utilisateurs :</strong> Les livres, 
              textes et images créés par les utilisateurs via notre plateforme leur appartiennent 
              intégralement. EI Glas25 ne revendique aucun droit de propriété sur les créations 
              des utilisateurs.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">5. Technologies utilisées</h2>
            <p>GlasEditionsLab utilise les technologies suivantes pour fournir ses services :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>Intelligence Artificielle :</strong> Google Gemini pour la génération de texte et d'images</li>
              <li><strong>Paiements sécurisés :</strong> Stripe pour le traitement des transactions</li>
              <li><strong>Authentification :</strong> Système JWT sécurisé et Google OAuth</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">6. Limitation de responsabilité</h2>
            <p>
              EI Glas25 s'efforce d'assurer au mieux de ses possibilités l'exactitude et la mise 
              à jour des informations diffusées sur le site, dont elle se réserve le droit de 
              corriger, à tout moment et sans préavis, le contenu.
            </p>
            <p className="mt-4">
              Toutefois, EI Glas25 ne peut garantir l'exactitude, la précision ou l'exhaustivité 
              des informations mises à disposition sur le site. En conséquence, EI Glas25 décline 
              toute responsabilité pour toute imprécision, inexactitude ou omission portant sur 
              des informations disponibles sur le site.
            </p>
            <p className="mt-4">
              EI Glas25 ne pourra être tenue responsable des dommages directs ou indirects 
              résultant de l'utilisation du site ou des contenus générés par l'intelligence 
              artificielle.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">7. Liens hypertextes</h2>
            <p>
              Le site GlasEditionsLab peut contenir des liens hypertextes vers d'autres sites 
              présents sur le réseau Internet. Les liens vers ces autres ressources vous font 
              quitter le site GlasEditionsLab.
            </p>
            <p className="mt-4">
              EI Glas25 n'est pas responsable et ne peut être tenue pour responsable du contenu 
              des pages web pointées vers ces liens, ni des modifications ou mises à jour qui 
              leur sont apportées.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">8. Données personnelles</h2>
            <p>
              Pour connaître notre politique de gestion des données personnelles, veuillez 
              consulter notre{" "}
              <Link to="/privacy" className="text-primary hover:underline">
                Politique de Confidentialité
              </Link>.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">9. Droit applicable</h2>
            <p>
              Les présentes mentions légales sont régies par le droit français. En cas de litige, 
              et après échec de toute tentative de recherche d'une solution amiable, les tribunaux 
              français seront seuls compétents pour connaître de ce litige.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">10. Contact</h2>
            <p>
              Pour toute question ou demande d'information concernant le site, vous pouvez 
              nous contacter :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>Par email :</strong> <a href="mailto:glaseditionslab@gmail.com" className="text-primary hover:underline">glaseditionslab@gmail.com</a></li>
              <li><strong>Par courrier :</strong> EI Glas25, 1 Ter rue du Cotay, 25300 Arçon, France</li>
            </ul>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-border mt-12">
        <div className="max-w-4xl mx-auto px-6 md:px-12 text-center text-sm text-muted-foreground">
          © 2025 GlasEditionsLab - EI Glas25
        </div>
      </footer>
    </div>
  );
}
