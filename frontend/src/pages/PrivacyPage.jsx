import { Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function PrivacyPage() {
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
        <h1 className="font-serif text-4xl font-bold mb-8">Politique de Confidentialité</h1>
        
        <div className="prose prose-stone max-w-none space-y-8">
          <p className="text-muted-foreground">Dernière mise à jour : Février 2026</p>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">1. Responsable du traitement</h2>
            <p>Le responsable du traitement des données personnelles est :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Raison sociale :</strong> EI Glas25</li>
              <li><strong>Adresse :</strong> 1 Ter rue du Cotay, 25300 Arçon, France</li>
              <li><strong>SIRET :</strong> 520 388 166 00024</li>
              <li><strong>Email :</strong> glas25@outlook.fr</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">2. Données collectées</h2>
            <p>Dans le cadre de l'utilisation de GlasEditionsLab, nous collectons les données suivantes :</p>
            
            <h3 className="font-semibold text-lg mt-4 mb-2">Données d'identification :</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Nom et prénom</li>
              <li>Adresse email</li>
              <li>Photo de profil (si connexion via Google)</li>
            </ul>

            <h3 className="font-semibold text-lg mt-4 mb-2">Données de paiement :</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Informations de paiement (traitées par Stripe, non stockées sur nos serveurs)</li>
              <li>Historique des transactions</li>
            </ul>

            <h3 className="font-semibold text-lg mt-4 mb-2">Données d'utilisation :</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Livres créés et leur contenu</li>
              <li>Préférences de génération</li>
              <li>Dates de connexion</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">3. Finalités du traitement</h2>
            <p>Vos données sont collectées pour :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Créer et gérer votre compte utilisateur</li>
              <li>Fournir les services de génération de livres</li>
              <li>Traiter les paiements et gérer les abonnements</li>
              <li>Vous contacter pour le support technique</li>
              <li>Améliorer nos services</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">4. Base légale du traitement</h2>
            <p>Le traitement de vos données repose sur :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>L'exécution du contrat :</strong> pour fournir nos services</li>
              <li><strong>Le consentement :</strong> pour l'utilisation de cookies non essentiels</li>
              <li><strong>L'intérêt légitime :</strong> pour l'amélioration de nos services</li>
              <li><strong>L'obligation légale :</strong> pour la conservation des factures</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">5. Durée de conservation</h2>
            <p>Conformément au RGPD, vos données sont conservées pendant :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Données de compte :</strong> pendant la durée de votre inscription + 3 ans après suppression</li>
              <li><strong>Données de paiement :</strong> 10 ans (obligation légale comptable)</li>
              <li><strong>Livres créés :</strong> pendant la durée de votre inscription</li>
              <li><strong>Logs de connexion :</strong> 1 an</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">6. Partage des données avec des tiers</h2>
            <p>Vos données peuvent être partagées avec :</p>
            
            <h3 className="font-semibold text-lg mt-4 mb-2">Stripe (traitement des paiements)</h3>
            <p>
              Stripe traite vos informations de paiement de manière sécurisée. 
              <a href="https://stripe.com/fr/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline ml-1">
                Politique de confidentialité Stripe
              </a>
            </p>

            <h3 className="font-semibold text-lg mt-4 mb-2">Google (authentification OAuth)</h3>
            <p>
              Si vous vous connectez via Google, certaines données de votre profil Google sont partagées.
              <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline ml-1">
                Politique de confidentialité Google
              </a>
            </p>

            <h3 className="font-semibold text-lg mt-4 mb-2">Google Gemini (génération IA)</h3>
            <p>
              Les idées et contenus que vous fournissez sont envoyés à l'API Google Gemini pour la génération.
              Ces données ne sont pas stockées par Google au-delà du traitement immédiat.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">7. Vos droits</h2>
            <p>Conformément au RGPD, vous disposez des droits suivants :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Droit d'accès :</strong> obtenir une copie de vos données</li>
              <li><strong>Droit de rectification :</strong> corriger vos données inexactes</li>
              <li><strong>Droit à l'effacement :</strong> supprimer vos données ("droit à l'oubli")</li>
              <li><strong>Droit à la portabilité :</strong> recevoir vos données dans un format structuré</li>
              <li><strong>Droit d'opposition :</strong> vous opposer au traitement de vos données</li>
              <li><strong>Droit à la limitation :</strong> limiter le traitement de vos données</li>
            </ul>
            <p className="mt-4">
              Pour exercer ces droits, contactez-nous à : 
              <a href="mailto:glas25@outlook.fr" className="text-primary hover:underline ml-1">glas25@outlook.fr</a>
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">8. Sécurité des données</h2>
            <p>
              Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour protéger 
              vos données contre tout accès non autorisé, modification, divulgation ou destruction :
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Chiffrement des données en transit (HTTPS/TLS)</li>
              <li>Mots de passe hashés avec bcrypt</li>
              <li>Tokens d'authentification JWT sécurisés</li>
              <li>Accès restreint aux bases de données</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">9. Cookies</h2>
            <p>
              GlasEditionsLab utilise des cookies essentiels pour le fonctionnement du site :
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>session_token :</strong> authentification de l'utilisateur (7 jours)</li>
              <li><strong>auth_token :</strong> token JWT pour les requêtes API</li>
            </ul>
            <p className="mt-4">
              Ces cookies sont strictement nécessaires au fonctionnement du service et ne peuvent pas être désactivés.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">10. Réclamation</h2>
            <p>
              Si vous estimez que le traitement de vos données constitue une violation du RGPD, 
              vous pouvez introduire une réclamation auprès de la CNIL :
            </p>
            <p className="mt-2">
              <strong>Commission Nationale de l'Informatique et des Libertés (CNIL)</strong><br />
              3 Place de Fontenoy, TSA 80715<br />
              75334 Paris Cedex 07<br />
              <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                www.cnil.fr
              </a>
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">11. Contact</h2>
            <p>
              Pour toute question relative à cette politique de confidentialité, contactez-nous à :
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
