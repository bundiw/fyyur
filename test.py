 from distutils.command.install_headers import install_headers


session.query((Venue).join((Show).filter_by(venue_id == Venue.id)).all()).all()
 Correction

 result = session.query(Venue).join(Show).filter_by(venue_id=Venue.id).all()

 session.query(Customer).join(Invoice).filter(Invoice.amount == 8500).all()

line 377,360,330,186,170 not done