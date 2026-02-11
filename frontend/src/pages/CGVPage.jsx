import { Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CGVPage() {
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
        <h1 className="font-serif text-4xl font-bold mb-8">Conditions Générales de Vente</h1>
        
        <div className="prose prose-stone max-w-none space-y-8">
          <p className="text-muted-foreground">Dernière mise à jour : Février 2026</p>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 1 - Informations légales</h2>
            <p>Le site GlasEditionsLab est édité par :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Raison sociale :</strong> EI Glas25</li>
              <li><strong>Adresse :</strong> 1 Ter rue du Cotay, 25300 Arçon, France</li>
              <li><strong>SIRET :</strong> 520 388 166 00024</li>
              <li><strong>Email :</strong> glas25@outlook.fr</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 2 - Objet</h2>
            <p>
              Les présentes Conditions Générales de Vente (CGV) régissent les relations contractuelles entre 
              EI Glas25 et tout utilisateur (ci-après "le Client") souhaitant utiliser les services de 
              génération de livres par intelligence artificielle proposés sur le site GlasEditionsLab.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 3 - Services proposés</h2>
            <p>GlasEditionsLab propose les services suivants :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Génération automatique de livres de fiction et non-fiction par IA</li>
              <li>Création de plans et chapitres personnalisés</li>
              <li>Génération de couvertures par IA (selon abonnement)</li>
              <li>Export en formats PDF, EPUB, HTML et TXT</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 4 - Tarifs et abonnements</h2>
            <p>Les tarifs en vigueur sont les suivants :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Plan Débutant :</strong> 27€/mois - 3 livres/mois, 15 chapitres max par livre</li>
              <li><strong>Plan Auteur :</strong> 57€/mois - 7 livres/mois, 30 chapitres max par livre, couvertures IA</li>
              <li><strong>Plan Écrivain :</strong> 97€/mois - Livres et chapitres illimités, couvertures IA</li>
              <li><strong>Livre unique :</strong> 9,90€ - 1 livre, 30 chapitres max, couverture IA incluse</li>
            </ul>
            <p className="mt-4">Les prix sont indiqués en euros TTC. EI Glas25 se réserve le droit de modifier ses tarifs à tout moment.</p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 5 - Droit de rétractation</h2>
            <p>
              Conformément à l'article L221-18 du Code de la consommation, le Client dispose d'un délai de 
              <strong> 14 jours</strong> à compter de la souscription pour exercer son droit de rétractation, 
              sans avoir à justifier de motifs ni à payer de pénalités.
            </p>
            <p className="mt-4">
              Toutefois, conformément à l'article L221-28 du Code de la consommation, le droit de rétractation 
              ne peut être exercé pour les contenus numériques fournis sur un support immatériel dont l'exécution 
              a commencé avec l'accord du consommateur.
            </p>
            <p className="mt-4">
              Pour exercer ce droit, le Client doit contacter EI Glas25 par email à l'adresse : glas25@outlook.fr
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 6 - Conditions de remboursement</h2>
            <p className="text-muted-foreground italic">
              [Section en cours de rédaction - Les conditions détaillées de remboursement seront ajoutées prochainement]
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 7 - Propriété intellectuelle</h2>
            <p>
              Les contenus générés par l'IA via GlasEditionsLab appartiennent au Client qui les a créés. 
              Le Client est libre d'utiliser, modifier, publier et commercialiser les livres générés.
            </p>
            <p className="mt-4">
              Le Client garantit que les idées et informations fournies pour la génération ne violent 
              aucun droit de propriété intellectuelle de tiers.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 8 - Limitation de responsabilité</h2>
            <p className="text-muted-foreground italic">
              [Section en cours de rédaction - Les limitations de responsabilité spécifiques seront ajoutées prochainement]
            </p>
            <p className="mt-4">
              EI Glas25 ne saurait être tenu responsable de l'utilisation faite par le Client des contenus générés.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 9 - Données personnelles</h2>
            <p>
              Le traitement des données personnelles est détaillé dans notre{" "}
              <Link to="/privacy" className="text-primary hover:underline">Politique de Confidentialité</Link>.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 10 - Droit applicable</h2>
            <p>
              Les présentes CGV sont soumises au droit français. En cas de litige, les tribunaux français 
              seront seuls compétents.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 11 - Contact</h2>
            <p>
              Pour toute question relative aux présentes CGV, vous pouvez nous contacter à l'adresse : 
              <a href="mailto:glas25@outlook.fr" className="text-primary hover:underline ml-1">glas25@outlook.fr</a>
            </p>
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
