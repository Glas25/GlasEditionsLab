import { Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CGUPage() {
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
        <h1 className="font-serif text-4xl font-bold mb-8">Conditions Générales d'Utilisation</h1>
        
        <div className="prose prose-stone max-w-none space-y-8">
          <p className="text-muted-foreground">Dernière mise à jour : Février 2026</p>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 1 - Objet</h2>
            <p>
              Les présentes Conditions Générales d'Utilisation (ci-après « CGU ») ont pour objet 
              de définir les modalités et conditions d'utilisation des services proposés sur le 
              site GlasEditionsLab (ci-après « le Site »), ainsi que de définir les droits et 
              obligations des parties dans ce cadre.
            </p>
            <p className="mt-4">
              Elles sont accessibles et imprimables à tout moment par un lien direct en bas de 
              la page d'accueil du Site.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 2 - Exploitant du Site</h2>
            <p>Le Site est exploité par :</p>
            <div className="bg-stone-50 p-6 rounded-sm mt-4">
              <ul className="list-none space-y-2 m-0 p-0">
                <li><strong>EI Glas25</strong></li>
                <li>1 Ter rue du Cotay, 25300 Arçon, France</li>
                <li>SIRET : 520 388 166 00024</li>
                <li>Email : <a href="mailto:glas25@outlook.fr" className="text-primary hover:underline">glas25@outlook.fr</a></li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 3 - Accès au Site</h2>
            <p>
              Le Site est accessible gratuitement en tout lieu à tout utilisateur ayant un accès 
              à Internet. Tous les frais supportés par l'utilisateur pour accéder au service 
              (matériel informatique, logiciels, connexion Internet, etc.) sont à sa charge.
            </p>
            <p className="mt-4">
              L'utilisateur non-membre n'a pas accès aux services réservés. Pour cela, il doit 
              s'inscrire en remplissant le formulaire prévu à cet effet. En acceptant de 
              s'inscrire aux services réservés, l'utilisateur membre s'engage à fournir des 
              informations sincères et exactes.
            </p>
            <p className="mt-4">
              Pour accéder aux services, l'utilisateur doit ensuite s'identifier à l'aide de 
              son identifiant (email) et de son mot de passe, ou via son compte Google.
            </p>
            <p className="mt-4">
              EI Glas25 se réserve le droit de refuser l'accès aux services, unilatéralement 
              et sans notification préalable, à tout utilisateur ne respectant pas les présentes 
              conditions d'utilisation.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 4 - Description des services</h2>
            <p>Le Site propose les services suivants :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>
                <strong>Génération de livres par IA :</strong> Création automatique de livres 
                de fiction et non-fiction à partir d'une idée initiale fournie par l'utilisateur
              </li>
              <li>
                <strong>Création de plans :</strong> Génération automatique de structures de 
                livres avec titres de chapitres et résumés
              </li>
              <li>
                <strong>Rédaction de chapitres :</strong> Génération du contenu textuel de 
                chaque chapitre selon le plan établi
              </li>
              <li>
                <strong>Génération de couvertures :</strong> Création d'images de couverture 
                par intelligence artificielle (selon abonnement)
              </li>
              <li>
                <strong>Export :</strong> Téléchargement des livres aux formats PDF, EPUB, 
                HTML et TXT
              </li>
              <li>
                <strong>Gestion de bibliothèque :</strong> Stockage et organisation des livres 
                créés par l'utilisateur
              </li>
            </ul>
            <p className="mt-4">
              EI Glas25 se réserve le droit de modifier, suspendre ou interrompre à tout moment, 
              temporairement ou définitivement, tout ou partie des services sans préavis et sans 
              que sa responsabilité puisse être engagée.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 5 - Utilisation de l'Intelligence Artificielle</h2>
            <p>
              Le Site utilise des technologies d'intelligence artificielle (Google Gemini) pour 
              générer du contenu textuel et des images. L'utilisateur reconnaît et accepte que :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>
                Le contenu généré par l'IA est créé de manière automatique et peut contenir 
                des imperfections, inexactitudes ou incohérences
              </li>
              <li>
                L'utilisateur est seul responsable de la vérification et de la validation du 
                contenu généré avant toute utilisation ou publication
              </li>
              <li>
                EI Glas25 ne garantit pas l'originalité absolue des contenus générés et 
                recommande aux utilisateurs de vérifier l'absence de plagiat avant publication
              </li>
              <li>
                Les contenus générés peuvent refléter des biais présents dans les données 
                d'entraînement de l'IA
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 6 - Propriété des contenus générés</h2>
            <p>
              Les livres, textes et images générés par l'utilisateur via le Site appartiennent 
              intégralement à l'utilisateur qui les a créés. L'utilisateur dispose de tous les 
              droits d'exploitation sur ses créations, incluant :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Le droit de reproduction</li>
              <li>Le droit de représentation</li>
              <li>Le droit de modification et d'adaptation</li>
              <li>Le droit de commercialisation et de distribution</li>
              <li>Le droit de publication sous son nom ou pseudonyme</li>
            </ul>
            <p className="mt-4">
              EI Glas25 ne revendique aucun droit de propriété sur les contenus créés par les 
              utilisateurs et ne les utilisera pas à des fins commerciales sans autorisation 
              explicite.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 7 - Responsabilités de l'utilisateur</h2>
            <p>L'utilisateur s'engage à :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>
                Ne pas utiliser le service pour générer du contenu illégal, diffamatoire, 
                obscène, pornographique, violent, raciste, xénophobe ou contraire aux bonnes mœurs
              </li>
              <li>
                Ne pas tenter de contourner les mesures de sécurité ou de protection du Site
              </li>
              <li>
                Ne pas utiliser le service de manière à surcharger, endommager ou altérer 
                le fonctionnement du Site
              </li>
              <li>
                Ne pas usurper l'identité d'une autre personne ou entité
              </li>
              <li>
                Respecter les droits de propriété intellectuelle de tiers
              </li>
              <li>
                Maintenir la confidentialité de ses identifiants de connexion
              </li>
            </ul>
            <p className="mt-4">
              L'utilisateur est seul responsable de l'utilisation qu'il fait du contenu généré 
              et des conséquences qui en découlent.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 8 - Limitation de responsabilité</h2>
            <p>
              EI Glas25 ne pourra être tenue responsable des dommages directs ou indirects 
              causés au matériel de l'utilisateur lors de l'accès au Site.
            </p>
            <p className="mt-4">
              EI Glas25 décline toute responsabilité quant à l'utilisation qui pourrait être 
              faite des informations et contenus présents sur le Site ou générés par le service.
            </p>
            <p className="mt-4">
              EI Glas25 s'engage à mettre en œuvre tous les moyens nécessaires pour assurer 
              la continuité et la qualité du service, mais ne peut garantir une disponibilité 
              permanente du Site.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 9 - Données personnelles</h2>
            <p>
              Le Site collecte des données personnelles nécessaires au fonctionnement des 
              services. Pour en savoir plus sur la collecte et le traitement de vos données, 
              veuillez consulter notre{" "}
              <Link to="/privacy" className="text-primary hover:underline">
                Politique de Confidentialité
              </Link>.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 10 - Propriété intellectuelle du Site</h2>
            <p>
              Tous les éléments du Site (structure, design, textes, graphismes, logos, icônes, 
              images, éléments sonores, logiciels, etc.) sont la propriété exclusive de EI Glas25 
              ou de ses partenaires et sont protégés par les lois relatives à la propriété 
              intellectuelle.
            </p>
            <p className="mt-4">
              Toute reproduction, représentation, modification, publication, adaptation de tout 
              ou partie des éléments du Site, quel que soit le moyen ou le procédé utilisé, 
              est interdite sauf autorisation écrite préalable de EI Glas25.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 11 - Suspension et résiliation</h2>
            <p>
              EI Glas25 se réserve le droit de suspendre ou de résilier l'accès d'un utilisateur 
              au Site, sans préavis ni indemnité, en cas de :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Non-respect des présentes CGU</li>
              <li>Utilisation frauduleuse ou abusive du service</li>
              <li>Fourniture d'informations fausses lors de l'inscription</li>
              <li>Non-paiement des services souscrits</li>
              <li>Comportement préjudiciable aux autres utilisateurs ou au Site</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 12 - Modification des CGU</h2>
            <p>
              EI Glas25 se réserve le droit de modifier les présentes CGU à tout moment. Les 
              utilisateurs seront informés de toute modification par un avis sur le Site. 
              L'utilisation continue du Site après modification des CGU vaut acceptation des 
              nouvelles conditions.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 13 - Droit applicable et juridiction</h2>
            <p>
              Les présentes CGU sont régies par le droit français. En cas de litige, et après 
              échec de toute tentative de résolution amiable, les tribunaux français seront 
              seuls compétents.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 14 - Contact</h2>
            <p>
              Pour toute question relative aux présentes CGU, vous pouvez nous contacter à 
              l'adresse : <a href="mailto:glas25@outlook.fr" className="text-primary hover:underline">glas25@outlook.fr</a>
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
