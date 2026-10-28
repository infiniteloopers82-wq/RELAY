import { ArrowRight, Boxes, CheckCircle2, Clock3, FlaskConical, Microscope, Printer, MoveUpRight, ShieldCheck, Sparkles, Warehouse, Wrench } from 'lucide-react';
import { Link } from 'react-router-dom';

const categories = [
  { name: 'Lab equipment', icon: Microscope, colour: 'coral', count: 'Equipment & tools' },
    { name: '3D printing', icon: Printer, colour: 'sky', count: 'Labs & makerspaces' },
    { name: 'Creative studios', icon: Sparkles, colour: 'lavender', count: 'Production spaces' },
    { name: 'Workshops', icon: Wrench, colour: 'yellow', count: 'Tools & benches' },
    { name: 'Science spaces', icon: FlaskConical, colour: 'teal', count: 'Research spaces' },
    { name: 'Shared rooms', icon: Warehouse, colour: 'sage', count: 'Rooms & venues' },
];

export default function Landing() {
  return (
    <div className="landing-page">
      <header className="landing-nav">
        <Link className="landing-brand" to="/" aria-label="RELAY home">
          <span className="landing-brand-mark"><Boxes size={21} /></span>
          RELAY
        </Link>
        <nav aria-label="Main navigation">
          <a href="#resources">Discover</a>
          <a href="#how-it-works">How it works</a>
          <a href="#trust">Trust & accountability</a>
        </nav>
        <div className="landing-nav-actions">
          <Link className="text-action" to="/login">Sign in</Link>
          <Link className="landing-button" to="/login">Explore RELAY <ArrowRight size={17} /></Link>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="hero-copy">
            <div className="eyebrow"><span /><span>Built for connected campuses</span></div>
            <h1>Share more.<br /><em>Waste less.</em><br />Trust every handover.</h1>
            <p>Discover the equipment, studios, and spaces already within your institution—then book them with transparent rules and accountable returns.</p>
            <div className="hero-actions">
              <Link className="landing-button large" to="/login">Find a resource <ArrowRight size={18} /></Link>
              <a className="play-link" href="#how-it-works"><span><Clock3 size={18} /></span> See how it works</a>
            </div>
            <div className="hero-proof">
              <div className="proof-avatars"><span>LS</span><span>MU</span><span>AK</span></div>
              <p><strong>Built for shared campuses</strong><br />with one connected community</p>
            </div>
          </div>

          <div className="hero-art" aria-label="A shared research lab resource">
            <div className="hero-blob" />
            <div className="hero-photo-wrap">
              <img src="https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1100&q=85" alt="Students collaborating in a modern laboratory" />
              <div className="photo-label"><span><FlaskConical size={17} /></span> Materials Science Lab</div>
            </div>
            <div className="floating-card booking-card">
              <div className="floating-icon coral"><CheckCircle2 size={19} /></div>
              <div><small>Booking approved</small><strong>Robotics Workshop</strong></div>
            </div>
            <div className="floating-card availability-card">
              <div className="mini-chart"><i /><i /><i /><i /></div>
              <div><strong>Live</strong><small>availability</small></div>
            </div>
            <div className="art-doodle"><Sparkles size={28} /></div>
          </div>
        </section>

        <section className="resource-section" id="resources">
          <div className="section-heading">
            <div><span className="section-kicker">Explore the network</span><h2>Resources with purpose</h2></div>
            <Link to="/login">View all resources <ArrowRight size={17} /></Link>
          </div>
          <div className="category-grid">
            {categories.map(({ name, icon: Icon, colour, count }) => (
              <Link className={`category-card ${colour}`} to="/login" key={name}>
                <div className="category-card-top"><span className="category-icon"><Icon size={25} /></span><MoveUpRight size={18} /></div>
                <strong>{name}</strong>
                <small>{count}</small>
              </Link>
            ))}
          </div>
        </section>

        <section className="featured-section">
          <div className="featured-image">
            <img src="https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1000&q=85" alt="Precision engineering equipment in a workshop" />
            <span className="featured-tag">Popular this week</span>
          </div>
          <div className="featured-copy">
            <span className="section-kicker">Made for discovery</span>
            <h2>The right tool should never be out of reach.</h2>
            <p>Search by location, category, eligibility, and availability. Every listing tells you exactly what you need to book responsibly.</p>
            <ul>
              <li><CheckCircle2 size={19} /> Clear eligibility requirements</li>
              <li><CheckCircle2 size={19} /> Live availability and fair waitlists</li>
              <li><CheckCircle2 size={19} /> Approval with a human decision trail</li>
            </ul>
            <Link className="landing-button dark" to="/login">Browse resources <ArrowRight size={17} /></Link>
          </div>
        </section>

        <section className="steps-section" id="how-it-works">
          <div className="steps-intro"><span className="section-kicker">Simple by design</span><h2>A better handover,<br />from request to return.</h2></div>
          <div className="steps-grid">
            <article><span>01</span><div className="step-icon blue"><SearchIcon /></div><h3>Discover</h3><p>Find equipment and spaces across departments, complete with access rules.</p></article>
            <article><span>02</span><div className="step-icon coral"><ShieldCheck /></div><h3>Request</h3><p>Share your purpose and confirm eligibility before submitting a booking.</p></article>
            <article><span>03</span><div className="step-icon gold"><CheckCircle2 /></div><h3>Handover</h3><p>Check in, document condition, use responsibly, then complete a clear return.</p></article>
          </div>
        </section>

        <section className="trust-section" id="trust">
          <div className="trust-panel">
            <div><span className="section-kicker light">Trust at every step</span><h2>Accountability without friction.</h2></div>
            <div className="trust-stat"><strong>Clear</strong><span>decision trail</span></div>
            <div className="trust-stat"><strong>Fair</strong><span>resource allocation</span></div>
            <div className="trust-stat"><strong>Shared</strong><span>accountability</span></div>
          </div>
        </section>

        <section className="closing-cta">
          <div><span className="section-kicker">Your campus, connected</span><h2>Ready to share what<br />your community can use?</h2></div>
          <Link className="landing-button large" to="/login">Start sharing <ArrowRight size={18} /></Link>
        </section>
      </main>

      <footer><div className="landing-brand"><span className="landing-brand-mark"><Boxes size={21} /></span>RELAY</div><p>Trusted resource sharing for your institution.</p><span>© 2026 RELAY</span></footer>
    </div>
  );
}

function SearchIcon() { return <Boxes size={24} />; }
